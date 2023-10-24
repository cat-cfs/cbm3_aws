import json
import boto3


def start_execution(
    execution_name: str, state_machine_arn: str, region_name: str, tasks: dict
) -> dict[str, str]:
    """Starts an execution on a cbm_aws cluster

    Args:
        execution_name (str): The name of the execution. This name must be
            unique for your AWS account, region, and state machine for 90 days.
            For more information, see Limits Related to State Machine
            Executions in the AWS Step Functions Developer Guide.
        state_machine_arn (str): AWS resource name for the state machine on
            which to run the execution.
        region_name (str): the region name
        tasks (dict): the input data for the execution

    Returns:
        dict: the return value of the boto3 state function client
            start_execution function.
    """
    sfn_client = boto3.client("stepfunctions", region_name=region_name)

    start_execution_response = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        name=execution_name,
        input=json.dumps(tasks),
    )
    return {str(k): str(v) for k, v in start_execution_response.items()}
