import json
import boto3
from cbm3_aws.namespace import Namespace


def start_execution(execution_name, state_machine_arn, region_name, tasks):
    sfn_client = boto3.client('stepfunctions', region_name=region_name)

    start_execution_response = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        name=execution_name,
        input=json.dumps(tasks))
