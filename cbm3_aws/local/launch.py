import boto3
import os
import json

client = boto3.client('stepfunctions')

response = client.create_activity(
    name='cbm3_run_task'
    # tags=[
    #    {
    #        'key': 'string',
    #        'value': 'string'
    #    },
    # ]
)


def get_local_dir():
    """Gets the directory containing this script
    Returns:
        str: full path to the the script's directory
    """
    return os.path.dirname(os.path.realpath(__file__))


def load_state_machine_definition(path, **template_kwargs):
    with open(path, 'r') as fp:
        # do a load/dump round trip to catch json syntax problems
        return json.load(fp)


def create_state_machines(role_arn, cloud_watch_logs_group_arn):

    cbm3_run_task_state_machine_definition = load_state_machine_definition(
        os.path.join(get_local_dir(), "cbm_run_state_machine.json"))

    cbm3_run_task_state_machine_response = client.create_state_machine(
        name='cbm3_run_task_state_machine',
        definition=cbm3_run_task_state_machine_definition,
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

    # TODO: template the cbm_run_state_machine defintion with the value of
    # cbm3_run_task_state_machine_response["stateMachineArn"]

    cbm3_run_state_machine_definition = load_state_machine_definition(
        os.path.join(get_local_dir(), "cbm_run_state_machine.json"),
        cbm3_run_task_state_machine_response["stateMachineArn"])

    response = client.create_state_machine(
        name='cbm3_run_state_machine',
        definition=cbm3_run_state_machine_definition,
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

def create_worker_activity():
    pass