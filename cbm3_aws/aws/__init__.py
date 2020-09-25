import boto3
from botocore.exceptions import ClientError
from cbm3_aws.aws import roles
from cbm3_aws.aws import step_functions
from cbm3_aws.aws import autoscale_group
from cbm3_aws.aws import s3_bucket


def __get_account_number(sts_client):
    return sts_client.get_caller_identity()["Account"]


def start_app():
    region_name = ""
    s3_bucket_name = ""
    n_instances = 10
    try:
        s3_client = boto3.client("s3", region_name=region_name)
        iam_client = boto3.client("iam", region_name=region_name)
        sts_client = boto3.client("sts", region_name=region_name)
        sfn_client = boto3.client('stepfunctions', region_name=region_name)

        s3_bucket.create_bucket(
            client=s3_client, bucket_name=s3_bucket_name, region=region_name)

        iam_role_context = roles.create_instance_iam_role(
            client=iam_client, s3_bucket_name=s3_bucket_name)

        state_machine_role_context = roles.create_state_machine_role(
            client=iam_client, account_number=__get_account_number(sts_client))

        state_machine_context = step_functions.create_state_machines(
            client=sfn_client, role_arn=state_machine_role_context.role_arn,
            max_concurrency=n_instances)

        autoscale_group.create_autoscaling_group()

    except ClientError as err:
        # from:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
        if err.response['Error']['Code'] == 'InternalError': # Generic error
            print('Error Message: {}'.format(err.response['Error']['Message']))
            print('Request ID: {}'.format(err.response['ResponseMetadata']['RequestId']))
            print('Http code: {}'.format(err.response['ResponseMetadata']['HTTPStatusCode']))
        else:
            raise err