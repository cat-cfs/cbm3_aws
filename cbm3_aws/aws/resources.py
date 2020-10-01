import os
import json
import boto3
from botocore.exceptions import ClientError

from cbm3_aws.instance.user_data import create_userdata
from cbm3_aws.aws import roles
from cbm3_aws.namespace import Namespace
from cbm3_aws.aws import step_functions
from cbm3_aws.aws import autoscale_group
from cbm3_aws.aws import s3_bucket
from cbm3_aws.aws.names import get_names
from cbm3_aws.aws.names import get_uuid
from cbm3_aws import log_helper


def __s3_bucket_exists(s3_client, bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        return False
    return True


def __get_account_number(sts_client):
    return sts_client.get_caller_identity()["Account"]


def __write_resources_file(resource_description, resource_description_path):
    with open(resource_description_path, 'w') as out_file:
        json.dump(resource_description.to_dict(), out_file, indent=4)


def cleanup(resource_description):
    """Cleans up all resources allocated by the :py:func:`deploy` method.

    Args:
        resource_description (Namespace): the return value of a call to
            the :py:func:`deploy` method which contains identifying
            information for AWS resources to deallocate.
    """
    rd = resource_description

    ec2_client = boto3.client("ec2", region_name=rd.region_name)
    auto_scale_client = boto3.client(
        'autoscaling', region_name=rd.region_name)
    iam_client = boto3.client("iam", region_name=rd.region_name)
    sfn_client = boto3.client('stepfunctions', region_name=rd.region_name)

    if "autoscale_group_context" in rd:
        autoscale_group.delete_autoscaling_group(
            client=auto_scale_client, context=rd.autoscale_group_context)
    if "launch_template_context" in rd:
        autoscale_group.delete_launch_template(
            client=ec2_client, context=rd.launch_template_context)
    if "state_machine_context" in rd:
        step_functions.cleanup(
            client=sfn_client, arn_context=rd.state_machine_context)

    if "state_machine_policy_context" in rd:
        roles.delete_policy(
            client=iam_client,
            policy_context=rd.state_machine_policy_context)
    if "s3_bucket_policy_context" in rd:
        roles.delete_policy(
            client=iam_client, policy_context=rd.s3_bucket_policy_context)

    if "state_machine_role_context" in rd:
        roles.delete_role(
            client=iam_client, role_context=rd.state_machine_role_context)
    if "instance_iam_role_context" in rd:
        roles.delete_instance_profile(client=iam_client, rd.instance_iam_role_context)
        roles.delete_role(
            client=iam_client, role_context=rd.instance_iam_role_context)


def deploy(region_name, s3_bucket_name, min_instances, max_instances,
           image_ami_id, instance_type, resource_description_path):
    logger = log_helper.get_logger()

    if os.path.exists(resource_description_path):
        raise ValueError(
            "specified resource_description_path already exists: "
            f"'{resource_description_path}'")

    # resource description
    rd = Namespace()
    rd.uuid = get_uuid()
    __write_resources_file(rd, resource_description_path)
    rd.names = get_names(rd.uuid)
    rd.region_name = region_name
    rd.s3_bucket_name = s3_bucket_name
    rd.min_instances = int(min_instances)
    rd.max_instances = int(max_instances)
    rd.image_ami_id = image_ami_id
    rd.instance_type = instance_type

    try:

        s3_client = boto3.client("s3", region_name=rd.region_name)
        ec2_client = boto3.client("ec2", region_name=rd.region_name)
        auto_scale_client = boto3.client(
            'autoscaling', region_name=rd.region_name)
        iam_client = boto3.client("iam", region_name=rd.region_name)
        sts_client = boto3.client("sts", region_name=rd.region_name)
        sfn_client = boto3.client('stepfunctions', region_name=rd.region_name)

        if not __s3_bucket_exists(s3_client, rd.s3_bucket_name):
            logger.info(f"creating s3 bucked {rd.s3_bucket_name}")
            s3_bucket.create_bucket(
                client=s3_client, bucket_name=rd.s3_bucket_name,
                region=rd.region_name)

        account_number = __get_account_number(sts_client)
        logger.info("creating policies")
        rd.s3_bucket_policy_context = roles.create_s3_bucket_policy(
            client=iam_client, s3_bucket_name=rd.s3_bucket_name)
        rd.state_machine_policy_context = roles.create_state_machine_policy(
            client=iam_client, account_number=account_number, names=rd.names)

        logger.info("creating iam roles")
        rd.instance_iam_role_context = roles.create_instance_iam_role(
            client=iam_client,
            policy_context_list=[
                rd.s3_bucket_policy_context,
                rd.state_machine_policy_context],
            names=rd.names)

        rd.state_machine_role_context = roles.create_state_machine_role(
            client=iam_client,
            policy_context_list=[rd.state_machine_policy_context],
            names=rd.names)

        rd.state_machine_context = step_functions.create_state_machines(
            client=sfn_client, role_arn=rd.state_machine_role_context.role_arn,
            max_concurrency=rd.max_instances, names=rd.names)

        rd.user_data = create_userdata(
            s3_bucket_name=rd.s3_bucket_name,
            activity_arn=rd.state_machine_context.activity_arn)

        rd.launch_template_context = autoscale_group.create_launch_template(
            client=ec2_client, name=rd.names.autoscale_launch_template,
            image_ami_id=rd.image_ami_id, instance_type=rd.instance_type,
            iam_instance_profile_arn=rd.instance_iam_role_context.role_arn,
            user_data=rd.user_data)

        rd.autoscale_group_context = autoscale_group.create_autoscaling_group(
            client=auto_scale_client, name=rd.names.autoscale_group,
            launch_template_context=rd.launch_template_context,
            min_size=rd.min_instances, max_size=rd.max_instances)

        return rd

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
    finally:
        __write_resources_file(rd, resource_description_path)
