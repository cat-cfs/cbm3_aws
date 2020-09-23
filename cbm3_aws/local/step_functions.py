from types import SimpleNamespace
import json
from contextlib import contextmanager

from cbm3_aws import constants
from cbm3_aws.local import cbm3_run_task_state_machine
from cbm3_aws.local import cbm3_run_state_machine


def _create_worker_activity(client, activity_task_name):
    response = client.create_activity(
        name=constants.CBM_RUN_ACTIVITY_NAME)
    return response["actvivityArn"]


def _create_task_state_machine(client, worker_activity_resource_arn, role_arn):

    state_machine_definition = cbm3_run_task_state_machine.get_state_machine(
        cbm_run_task_activity_arn=worker_activity_resource_arn)

    response = client.create_state_machine(
        name='cbm3_run_task_state_machine',
        definition=state_machine_definition,
        roleArn=role_arn,
        type='STANDARD')

    return response["stateMachineArn"]


def _create_application_state_machine(client, task_state_machine_arn,
                                      role_arn, max_concurrency):

    state_machine_definition = cbm3_run_state_machine.get_state_machine(
        task_state_machine_arn=task_state_machine_arn,
        max_concurrency=max_concurrency)

    cbm3_run_state_machine_response = client.create_state_machine(
        name='cbm3_run_state_machine',
        definition=state_machine_definition,
        roleArn=role_arn,
        type='STANDARD')

    return cbm3_run_state_machine_response["stateMachineArn"]


@contextmanager
def _create_state_machines(client, activity_task_name, role_arn,
                           max_concurrency):

    try:
        activity_arn = _create_worker_activity(
            client=client, activity_task_name=activity_task_name)
        task_state_machine_arn = _create_task_state_machine(
            client=client, worker_activity_resource_arn=activity_arn,
            role_arn=role_arn)
        app_state_machine_arn = _create_application_state_machine(
            client=client, task_state_machine_arn=task_state_machine_arn,
            role_arn=role_arn, max_concurrency=max_concurrency)
        arn_context = SimpleNamespace(
            client=client, activity_arn=activity_arn,
            task_state_machine_arn=task_state_machine_arn,
            app_state_machine_arn=app_state_machine_arn)
        yield arn_context
    finally:
        _cleanup(arn_context)


def _cleanup(client, arn_context):

    client.delete_state_machine(
        stateMachineArn=arn_context.app_state_machine_arn)
    client.delete_state_machine(
        stateMachineArn=arn_context.task_state_machine_arn)
    client.delete_activity(
        activityArn=arn_context.activity_arn)


def _start_execution(client, name, arn_context, task_list):
    client.start_execution(
        stateMachineArn=arn_context.app_state_machine_arn,
        name=name,
        input=json.dumps(task_list))


def run(client, role_arn, task_list, mask_task_concurrency):

    # import boto3
    # client = boto3.client('stepfunctions')
    execution_name = ""
    task_list = []
    with _create_state_machines(client, role_arn,
                                mask_task_concurrency) as arn_context:
        _start_execution(client, execution_name, arn_context, task_list)
