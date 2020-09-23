import boto3
import os
from types import SimpleNamespace
import json

client = boto3.client('stepfunctions')


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


def create_worker_activity(activity_task_name):
    response = client.create_activity(
        name=activity_task_name
        # tags=[
        #    {
        #        'key': 'string',
        #        'value': 'string'
        #    },
        # ]
        )
    return response["actvivityArn"]


def create_task_state_machine(worker_activity_resource_arn, role_arn,
                              cloud_watch_logs_group_arn):

    state_machine_definition = load_state_machine_definition(
        os.path.join(get_local_dir(), "cbm_run_state_machine.json"),
        worker_activity_resource_arn=worker_activity_resource_arn)

    response = client.create_state_machine(
        name='cbm3_run_task_state_machine',
        definition=state_machine_definition,
        roleArn=role_arn,
        type='STANDARD',
        loggingConfiguration={
            'level': 'ALL',
            'includeExecutionData': True,
            'destinations': [
                {
                    'cloudWatchLogsLogGroup': {
                        'logGroupArn': cloud_watch_logs_group_arn
                    }
                },
            ]
        }
        # tags=[
        #    {
        #        'key': 'string',
        #        'value': 'string'
        #    },
        # ]
        # tracingConfiguration={
        #    'enabled': True
        # }
    )

    return response["stateMachineArn"]


def create_application_state_machine(task_state_machine_arn, role_arn,
                                     cloud_watch_logs_group_arn):
    # TODO: template the cbm_run_state_machine defintion with the value of
    # cbm3_run_task_state_machine_response["stateMachineArn"]

    state_machine_definition = load_state_machine_definition(
        os.path.join(get_local_dir(), "cbm_run_state_machine.json"),
        task_state_machine_arn=task_state_machine_arn)

    cbm3_run_state_machine_response = client.create_state_machine(
        name='cbm3_run_state_machine',
        definition=state_machine_definition,
        roleArn=role_arn,
        type='STANDARD',
        loggingConfiguration={
            'level': 'ALL',
            'includeExecutionData': True,
            'destinations': [
                {
                    'cloudWatchLogsLogGroup': {
                        'logGroupArn': cloud_watch_logs_group_arn
                    }
                },
            ]
        }
        # tags=[
        #    {
        #        'key': 'string',
        #        'value': 'string'
        #    },
        # ]
        # tracingConfiguration={
        #    'enabled': True
        # }
    )

    return cbm3_run_state_machine_response["stateMachineArn"]


def create_state_machines(role_arn, cloud_watch_logs_group_arn):

    activity_arn = create_worker_activity(
        activity_task_name="cbm_run_task_activity")
    task_state_machine_arn = create_task_state_machine(
        worker_activity_resource_arn=activity_arn,
        role_arn=role_arn,
        cloud_watch_logs_group_arn=cloud_watch_logs_group_arn)
    app_state_machine_arn = create_application_state_machine(
        task_state_machine_arn=task_state_machine_arn,
        role_arn=role_arn,
        cloud_watch_logs_group_arn=cloud_watch_logs_group_arn)
    return SimpleNamespace(
        activity_arn=activity_arn,
        task_state_machine_arn=task_state_machine_arn,
        app_state_machine_arn=app_state_machine_arn)


def cleanup(arn_context):
    # todo delete the value returned by create_state_machines above
    pass
