from types import SimpleNamespace
import json
from cbm3_aws.local import cbm3_run_task_state_machine
from cbm3_aws.local import cbm3_run_state_machine


def _create_worker_activity(client, names):
    response = client.create_activity(
        name=names.run_activity)
    return response["activityArn"]


def _create_task_state_machine(client, worker_activity_resource_arn, role_arn,
                               names):

    state_machine_definition = cbm3_run_task_state_machine.get_state_machine(
        cbm_run_task_activity_arn=worker_activity_resource_arn)

    response = client.create_state_machine(
        name=names.run_task_state_machine,
        definition=state_machine_definition,
        roleArn=role_arn,
        type='STANDARD')

    return response["stateMachineArn"]


def _create_application_state_machine(client, task_state_machine_arn,
                                      role_arn, max_concurrency, names):

    state_machine_definition = cbm3_run_state_machine.get_state_machine(
        task_state_machine_arn=task_state_machine_arn,
        max_concurrency=max_concurrency)

    cbm3_run_state_machine_response = client.create_state_machine(
        name=names.run_state_machine,
        definition=state_machine_definition,
        roleArn=role_arn,
        type='STANDARD')

    return cbm3_run_state_machine_response["stateMachineArn"]


def create_state_machines(client, role_arn,
                          max_concurrency, names):
    """Create the state machine for running tasks on instances

    Args:
        client (SFN.client): boto3 step functions client
        role_arn (str): The Amazon Resource Name (ARN) of the IAM
            role to use for this state machine.
        max_concurrency (int): the maximum number of tasks to run
            concurrently
        names (namespace): the names used to label provisioned aws resources

    Returns:
        namespace: context object containing AWS state machine identifying
            information
    """

    activity_arn = _create_worker_activity(client=client, names=names)
    task_state_machine_arn = _create_task_state_machine(
        client=client, worker_activity_resource_arn=activity_arn,
        role_arn=role_arn, names=names)
    app_state_machine_arn = _create_application_state_machine(
        client=client, task_state_machine_arn=task_state_machine_arn,
        role_arn=role_arn, max_concurrency=max_concurrency, names=names)
    state_machine_context = SimpleNamespace(
        client=client, activity_arn=activity_arn,
        task_state_machine_arn=task_state_machine_arn,
        app_state_machine_arn=app_state_machine_arn)
    return state_machine_context


def cleanup(client, arn_context):

    client.delete_state_machine(
        stateMachineArn=arn_context.app_state_machine_arn)
    client.delete_state_machine(
        stateMachineArn=arn_context.task_state_machine_arn)
    client.delete_activity(
        activityArn=arn_context.activity_arn)


def start_execution(client, name, state_machine_context, tasks):
    client.start_execution(
        stateMachineArn=state_machine_context.app_state_machine_arn,
        name=name,
        input=json.dumps(tasks))
