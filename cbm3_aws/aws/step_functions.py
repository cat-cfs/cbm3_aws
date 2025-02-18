from cbm3_aws.aws import cbm3_run_task_state_machine
from cbm3_aws.aws import cbm3_run_state_machine
from mypy_boto3_stepfunctions.client import SFNClient


def _create_worker_activity(client: SFNClient, names: dict[str, str]) -> str:
    response = client.create_activity(name=names["run_activity"])
    return response["activityArn"]


def _create_task_state_machine(
    client: SFNClient,
    worker_activity_resource_arn: str,
    role_arn: str,
    names: dict[str, str],
) -> str:
    state_machine_definition = cbm3_run_task_state_machine.get_state_machine(
        cbm_run_task_activity_arn=worker_activity_resource_arn
    )

    response = client.create_state_machine(
        name=names["run_task_state_machine"],
        definition=state_machine_definition,
        roleArn=role_arn,
        type="STANDARD",
    )

    return response["stateMachineArn"]


def _create_application_state_machine(
    client: SFNClient,
    task_state_machine_arn: str,
    role_arn: str,
    names: dict[str, str],
) -> str:
    state_machine_definition = cbm3_run_state_machine.get_state_machine(
        task_state_machine_arn=task_state_machine_arn
    )

    cbm3_run_state_machine_response = client.create_state_machine(
        name=names["run_state_machine"],
        definition=state_machine_definition,
        roleArn=role_arn,
        type="STANDARD",
    )

    return cbm3_run_state_machine_response["stateMachineArn"]


def create_state_machines(
    client: SFNClient, role_arn: str, names: dict[str, str]
) -> dict:
    """Create the state machine for running tasks on instances

    Args:
        client (SFNClient): boto3 step functions client
        role_arn (str): The Amazon Resource Name (ARN) of the IAM
            role to use for this state machine.
        names (dict): the names used to label provisioned aws resources

    Returns:
        dict: dict containing AWS state machine identifying
            information
    """
    ctx = {}
    ctx["activity_arn"] = _create_worker_activity(client=client, names=names)
    ctx["task_state_machine_arn"] = _create_task_state_machine(
        client=client,
        worker_activity_resource_arn=ctx["activity_arn"],
        role_arn=role_arn,
        names=names,
    )
    ctx["app_state_machine_arn"] = _create_application_state_machine(
        client=client,
        task_state_machine_arn=ctx["task_state_machine_arn"],
        role_arn=role_arn,
        names=names,
    )

    return ctx


def cleanup(client: SFNClient, arn_context: dict[str, str]) -> None:
    if "activity_arn" in arn_context:
        client.delete_activity(activityArn=arn_context["activity_arn"])
    if "task_state_machine_arn" in arn_context:
        client.delete_state_machine(
            stateMachineArn=arn_context["task_state_machine_arn"]
        )
    if "app_state_machine_arn" in arn_context:
        client.delete_state_machine(
            stateMachineArn=arn_context["app_state_machine_arn"]
        )
