from types import SimpleNamespace
import json
from cbm3_aws import constants
from cbm3_aws.local import cbm3_run_task_state_machine
from cbm3_aws.local import cbm3_run_state_machine


def _create_worker_activity(client):
    response = client.create_activity(
        name=constants.CBM_RUN_ACTIVITY_NAME)
    return response["activityArn"]


def _create_task_state_machine(client, worker_activity_resource_arn, role_arn):

    state_machine_definition = cbm3_run_task_state_machine.get_state_machine(
        cbm_run_task_activity_arn=worker_activity_resource_arn)

    response = client.create_state_machine(
        name=constants.CBM3_RUN_TASK_STATE_MACHINE_NAME,
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
        name=constants.CBM3_RUN_STATE_MACHINE_NAME,
        definition=state_machine_definition,
        roleArn=role_arn,
        type='STANDARD')

    return cbm3_run_state_machine_response["stateMachineArn"]


def create_state_machines(client, role_arn,
                          max_concurrency):

    activity_arn = _create_worker_activity(client=client)
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
    return arn_context


def cleanup(client, arn_context):

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


#def run(client, role_arn, execution_name, max_task_concurrency, tasks):
#    """Start step functions to run concurrent CBM3 tasks
#
#    Args:
#        client (SFN.client): boto3 step functions client
#        role_arn (string): The Amazon Resource Name (ARN) of the IAM role to
#            use for the state machines created by this function.
#        execution_name (string): The name of the execution. This name must be
#            unique for your AWS account, region, and state machine for 90 days.
#        tasks (dict): the CBM3 tasks to run
#        max_task_concurrency (int): the maximum number of workers to run
#            concurrently.
#
#    Example::
#
#        run(
#            client=boto3.client('stepfunctions'),
#            role_arn='roleArn',
#            max_task_concurrency=2,
#            tasks = {
#                "task_list": [
#                    [
#                        {"project_code": "AB", "simulation_ids": [1, 2]},
#                        {"project_code": "BCB", "simulation_ids": [21, 22]}
#                    ],
#                    [
#                        {"project_code": "AB", "simulation_ids": [3, 4]},
#                        {"project_code": "BCB", "simulation_ids": [23, 24]}
#                    ]
#                ]
#            }
#        )
#
#    Yields:
#        object: an object containing named ARN for the step function resources
#    """
#    arn_context = _create_state_machines(
#        client, role_arn, max_task_concurrency)
#    _start_execution(client, execution_name, arn_context, tasks)
#    try:
#        yield arn_context
#    finally:
#        _cleanup(client, arn_context)
