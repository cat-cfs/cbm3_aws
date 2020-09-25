from types import SimpleNamespace
import boto3
from botocore.exceptions import ClientError
from cbm3_aws.aws import roles
from cbm3_aws.aws import step_functions
from cbm3_aws.aws import autoscale_group
from cbm3_aws.aws import s3_bucket


def __get_account_number(sts_client):
    return sts_client.get_caller_identity()["Account"]


def start():
    region_name = ""
    s3_bucket_name = ""
    n_instances = 10
    image_ami_id = ""
    instance_type = ""
    user_data = ""
    execution_name = ""
    tasks = {}
    try:
        s3_client = boto3.client("s3", region_name=region_name)
        ec2_client = boto3.client("ec2")  # region_name=region_name)
        auto_scale_client = boto3.client(
            'autoscaling', region_name=region_name)
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

        launch_template_context = autoscale_group.create_launch_template(
            client=ec2_client, image_ami_id=image_ami_id,
            instance_type=instance_type,
            iam_instance_profile_arn=iam_role_context.role_arn,
            user_data=user_data)

        autoscale_group_context = autoscale_group.create_autoscaling_group(
            client=auto_scale_client,
            launch_template_context=launch_template_context,
            size=n_instances)

        step_functions.start_execution(
            client=sfn_client, name=execution_name,
            state_machine_context=state_machine_context, tasks=tasks)

        return SimpleNamespace(
            region_name=region_name,
            s3_bucket_name=s3_bucket_name,
            n_instances=n_instances,
            image_ami_id=image_ami_id,
            instance_type=instance_type,
            user_data=user_data,
            execution_name=execution_name,
            tasks=tasks,
            iam_role_context=iam_role_context,
            state_machine_role_context=state_machine_role_context,
            state_machine_context=state_machine_context,
            launch_template_context=launch_template_context,
            autoscale_group_context=autoscale_group_context)

    except ClientError as err:
        # from:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
        if err.response['Error']['Code'] == 'InternalError':  # Generic error
            print('Error Message: {}'.format(err.response['Error']['Message']))
            print('Request ID: {}'.format(err.response['ResponseMetadata']['RequestId']))
            print('Http code: {}'.format(err.response['ResponseMetadata']['HTTPStatusCode']))
        else:
            raise err