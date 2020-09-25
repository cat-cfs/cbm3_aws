from types import SimpleNamespace
import boto3
from botocore.exceptions import ClientError
from cbm3_aws.instance.user_data import create_userdata
from cbm3_aws.aws import roles

from cbm3_aws.aws import step_functions
from cbm3_aws.aws import autoscale_group
from cbm3_aws.aws import s3_bucket
from cbm3_aws.aws.names import get_names
from cbm3_aws import log_helper


def __get_account_number(sts_client):
    return sts_client.get_caller_identity()["Account"]


def deploy(region_name, s3_bucket_name, n_instances, image_ami_id,
           instance_type):
    logger = log_helper.get_logger()
    try:
        names = get_names()
        s3_client = boto3.client("s3", region_name=region_name)
        ec2_client = boto3.client("ec2")  # region_name=region_name)
        auto_scale_client = boto3.client(
            'autoscaling', region_name=region_name)
        iam_client = boto3.client("iam", region_name=region_name)
        sts_client = boto3.client("sts", region_name=region_name)
        sfn_client = boto3.client('stepfunctions', region_name=region_name)

        logger.info(f"creating s3 bucked {s3_bucket_name}")
        s3_bucket.create_bucket(
            client=s3_client, bucket_name=s3_bucket_name, region=region_name)

        account_number = __get_account_number(sts_client)
        logger.info("creating policies")
        s3_bucket_policy_context = roles.create_s3_bucket_policy(
            client=iam_client, s3_bucket_name=s3_bucket_name)
        state_machine_policy_context = roles.create_state_machine_policy(
            client=iam_client, account_number=account_number, names=names)
        autoscale_update_policy = roles.create_autoscaling_group_policy(
            client=iam_client, account_number=account_number, names=names)

        logger.info("creating iam roles")
        instance_iam_role_context = roles.create_instance_iam_role(
            client=iam_client,
            policy_context_list=[
                s3_bucket_policy_context,
                state_machine_policy_context,
                autoscale_update_policy])

        state_machine_role_context = roles.create_state_machine_role(
            client=iam_client,
            policy_context_list=[state_machine_policy_context])

        state_machine_context = step_functions.create_state_machines(
            client=sfn_client, role_arn=state_machine_role_context.role_arn,
            max_concurrency=n_instances, names=names)

        user_data = create_userdata(
            s3_bucket_name=s3_bucket_name,
            activity_arn=state_machine_context.activity_arn)

        launch_template_context = autoscale_group.create_launch_template(
            client=ec2_client, image_ami_id=image_ami_id,
            instance_type=instance_type,
            iam_instance_profile_arn=instance_iam_role_context.role_arn,
            user_data=user_data)

        autoscale_group_context = autoscale_group.create_autoscaling_group(
            client=auto_scale_client,
            launch_template_context=launch_template_context,
            size=n_instances)

        return SimpleNamespace(
            names=names,
            region_name=region_name,
            s3_bucket_name=s3_bucket_name,
            n_instances=n_instances,
            image_ami_id=image_ami_id,
            instance_type=instance_type,
            user_data=user_data,
            s3_bucket_policy_context=s3_bucket_policy_context,
            state_machine_policy_context=state_machine_policy_context,
            instance_iam_role_context=instance_iam_role_context,
            state_machine_role_context=state_machine_role_context,
            state_machine_context=state_machine_context,
            launch_template_context=launch_template_context,
            autoscale_group_context=autoscale_group_context)

    except ClientError as err:
        # from:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
        if err.response['Error']['Code'] == 'InternalError':  # Generic error
            logger.error(
                'Error Message: {}'.format(
                    err.response['Error']['Message']))
            logger.error(
                'Request ID: {}'.format(
                    err.response['ResponseMetadata']['RequestId']))
            logger.error(
                'Http code: {}'.format(
                    err.response['ResponseMetadata']['HTTPStatusCode']))
        else:
            raise err
