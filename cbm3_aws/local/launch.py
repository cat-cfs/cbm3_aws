import os
from types import SimpleNamespace
import json
from contextlib import contextmanager

from cbm3_aws import constants


def get_local_dir():
    """Gets the directory containing this script
    Returns:
        str: full path to the the script's directory
    """
    return os.path.dirname(os.path.realpath(__file__))


def load_state_machine_definition(path, **template_kwargs):
    # TODO: implement templating
    with open(path, 'r') as fp:
        # do a load/dump round trip to catch json syntax problems
        return json.load(fp)


def create_worker_activity(client, activity_task_name):
    response = client.create_activity(
        name=activity_task_name)
    return response["actvivityArn"]


def create_task_state_machine(client, worker_activity_resource_arn, role_arn):

    state_machine_definition = load_state_machine_definition(
        os.path.join(get_local_dir(), "cbm_run_state_machine.json"),
        worker_activity_resource_arn=worker_activity_resource_arn)

    response = client.create_state_machine(
        name='cbm3_run_task_state_machine',
        definition=state_machine_definition,
        roleArn=role_arn,
        type='STANDARD')

    return response["stateMachineArn"]


def create_application_state_machine(client, task_state_machine_arn, role_arn):

    state_machine_definition = load_state_machine_definition(
        os.path.join(get_local_dir(), "cbm_run_state_machine.json"),
        task_state_machine_arn=task_state_machine_arn)

    cbm3_run_state_machine_response = client.create_state_machine(
        name='cbm3_run_state_machine',
        definition=state_machine_definition,
        roleArn=role_arn,
        type='STANDARD')

    return cbm3_run_state_machine_response["stateMachineArn"]


@contextmanager
def create_state_machines(client, activity_task_name, role_arn,
                          cloud_watch_logs_group_arn):

    try:
        activity_arn = create_worker_activity(
            client=client, activity_task_name=activity_task_name)
        task_state_machine_arn = create_task_state_machine(
            client=client, worker_activity_resource_arn=activity_arn,
            role_arn=role_arn,
            cloud_watch_logs_group_arn=cloud_watch_logs_group_arn)
        app_state_machine_arn = create_application_state_machine(
            client=client, task_state_machine_arn=task_state_machine_arn,
            role_arn=role_arn,
            cloud_watch_logs_group_arn=cloud_watch_logs_group_arn)
        arn_context = SimpleNamespace(
            client=client, activity_arn=activity_arn,
            task_state_machine_arn=task_state_machine_arn,
            app_state_machine_arn=app_state_machine_arn)
        yield arn_context
    finally:
        cleanup(arn_context)


def cleanup(client, arn_context):
    # todo delete the value returned by create_state_machines above
    client.delete_state_machine(
        stateMachineArn=arn_context.app_state_machine_arn)
    client.delete_state_machine(
        stateMachineArn=arn_context.task_state_machine_arn)
    client.delete_activity(
        activityArn=arn_context.activity_arn)


def start_execution(client, name, arn_context, task_list):
    client.start_execution(
        stateMachineArn=arn_context.app_state_machine_arn,
        name=name,
        input=json.dumps(task_list))


def run_app(client, role_arn, task_list):
    # import boto3
    # client = boto3.client('stepfunctions')
    activity_task_name = constants.CBM_RUN_ACTIVITY_NAME
    execution_name = ""
    task_list = []
    with create_state_machines(client, activity_task_name,
                               role_arn) as arn_context:

        start_execution(client, execution_name, arn_context, task_list)
