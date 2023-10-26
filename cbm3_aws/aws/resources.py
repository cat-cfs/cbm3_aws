import os
import json
import time
from typing import Union
import boto3
from botocore.exceptions import ClientError

from cbm3_aws.instance.user_data import create_userdata
from cbm3_aws.aws import roles
from cbm3_aws.aws import step_functions
from cbm3_aws.aws import autoscale_group
from cbm3_aws.aws import s3_bucket
from mypy_boto3_s3.literals import BucketLocationConstraintType
from mypy_boto3_sts.client import STSClient
from mypy_boto3_s3.client import S3Client
from cbm3_aws.aws.names import get_names
from cbm3_aws.aws.names import get_uuid
from cbm3_aws import log_helper

logger = log_helper.get_logger(__name__)


def _s3_bucket_exists(s3_client: S3Client, bucket_name: str) -> bool:
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        return False
    return True


def _get_account_number(sts_client: STSClient) -> str:
    return sts_client.get_caller_identity()["Account"]


def _write_resources_file(
    resource_description: dict, resource_description_path: str
) -> None:
    with open(resource_description_path, "w") as out_file:
        json.dump(resource_description, out_file, indent=4)


def cleanup(resource_description: dict) -> None:
    """Cleans up all resources allocated by the :py:func:`deploy` method.

    Args:
        resource_description (dict): the return value of a call to
            the :py:func:`deploy` method which contains identifying
            information for AWS resources to deallocate.
    """

    rd = resource_description

    logger.info("connecting")
    ec2_client = boto3.client(
        "ec2", region_name=rd["region_name"], verify=False
    )

    auto_scale_client = boto3.client(
        "autoscaling", region_name=rd["region_name"], verify=False
    )
    iam_client = boto3.client(
        "iam", region_name=rd["region_name"], verify=False
    )
    sfn_client = boto3.client(
        "stepfunctions", region_name=rd["region_name"], verify=False
    )

    if "autoscale_group_context" in rd:
        logger.info("drop autoscale group")
        autoscale_group.delete_autoscaling_group(
            client=auto_scale_client, context=rd["autoscale_group_context"]
        )
    if "launch_template_context" in rd:
        logger.info("drop launch template")
        autoscale_group.delete_launch_template(
            client=ec2_client, context=rd["launch_template_context"]
        )
    if "state_machine_context" in rd:
        logger.info("drop state machine")
        step_functions.cleanup(
            client=sfn_client, arn_context=rd["state_machine_context"]
        )

    logger.info("drop policies")
    if "state_machine_policy_context" in rd:
        roles.delete_policy(
            client=iam_client,
            policy_context=rd["state_machine_policy_context"],
        )
    if "ec2_worker_policy" in rd:
        roles.delete_policy(
            client=iam_client, policy_context=rd["ec2_worker_policy"]
        )

    logger.info("drop roles")
    if "state_machine_role_context" in rd:
        roles.delete_role(
            client=iam_client, role_context=rd["state_machine_role_context"]
        )
    if "instance_iam_role_context" in rd:
        roles.delete_instance_profile(
            client=iam_client, role_context=rd["instance_iam_role_context"]
        )
        roles.delete_role(
            client=iam_client, role_context=rd["instance_iam_role_context"]
        )


def deploy(
    region_name: BucketLocationConstraintType,
    s3_bucket_name: str,
    min_virtual_cpu: int,
    max_virtual_cpu: int,
    image_ami_id: str,
    resource_description_path: str,
    vpc_zone_identifier: Union[str, None] = None,
) -> dict:
    if os.path.exists(resource_description_path):
        raise ValueError(
            "specified resource_description_path already exists: "
            f"'{resource_description_path}'"
        )

    # resource description
    rd = {}
    rd["uuid"] = get_uuid()
    _write_resources_file(rd, resource_description_path)
    rd["names"] = get_names(rd["uuid"])
    rd["region_name"] = region_name
    rd["s3_bucket_name"] = s3_bucket_name
    rd["min_virtual_cpu"] = int(min_virtual_cpu)
    rd["max_virtual_cpu"] = int(max_virtual_cpu)
    rd["image_ami_id"] = image_ami_id

    try:
        logger.info("connecting")
        s3_client = boto3.client("s3", region_name=region_name, verify=False)
        ec2_client = boto3.client("ec2", region_name=region_name, verify=False)
        auto_scale_client = boto3.client(
            "autoscaling", region_name=region_name, verify=False
        )
        iam_client = boto3.client("iam", region_name=region_name, verify=False)
        sts_client = boto3.client("sts", region_name=region_name, verify=False)
        sfn_client = boto3.client(
            "stepfunctions", region_name=region_name, verify=False
        )

        logger.info("check if bucket exists")
        if not _s3_bucket_exists(s3_client, s3_bucket_name):
            logger.info(f"creating s3 bucket {s3_bucket_name}")
            s3_bucket.create_bucket(
                client=s3_client,
                bucket_name=s3_bucket_name,
                region=region_name,
            )

        account_number = _get_account_number(sts_client)
        logger.info("creating policies")
        rd["ec2_worker_policy"] = roles.create_ec2_worker_policy(
            client=iam_client,
            s3_bucket_name=s3_bucket_name,
            account_number=account_number,
            names=rd["names"],
        )
        rd["state_machine_policy_context"] = roles.create_state_machine_policy(
            client=iam_client, account_number=account_number, names=rd["names"]
        )

        logger.info("creating iam roles")
        rd["instance_iam_role_context"] = roles.create_instance_iam_role(
            client=iam_client,
            policy_context_list=[rd["ec2_worker_policy"]],
            names=rd["names"],
        )

        logger.info("creating state machine role")
        rd["state_machine_role_context"] = roles.create_state_machine_role(
            client=iam_client,
            policy_context_list=[rd["state_machine_policy_context"]],
            names=rd["names"],
        )

        # https://github.com/hashicorp/terraform/issues/15341
        # need to add a delay for the iam changes above to be processed
        # internally by AWS
        wait_time = 20
        logger.info(
            f"waiting {wait_time} seconds for changes to take effect on AWS"
        )
        time.sleep(wait_time)

        logger.info("creating state machine")
        rd["state_machine_context"] = step_functions.create_state_machines(
            client=sfn_client,
            role_arn=rd["state_machine_role_context"]["role_arn"],
            names=rd["names"],
        )

        logger.info("creating userdata")
        rd["user_data"] = create_userdata(
            s3_bucket_name=rd["s3_bucket_name"],
            activity_arn=rd["state_machine_context"]["activity_arn"],
            region_name=rd["region_name"],
        )

        iam_instance_profile_arn = rd["instance_iam_role_context"][
            "instance_profile_arn"
        ]

        logger.info("creating launch template")
        rd["launch_template_context"] = autoscale_group.create_launch_template(
            client=ec2_client,
            name=rd["names"]["autoscale_launch_template"],
            image_ami_id=image_ami_id,
            iam_instance_profile_arn=iam_instance_profile_arn,
            user_data=rd["user_data"],
        )

        availability_zones = None
        if not vpc_zone_identifier:
            logger.info("getting availability zones")
            availability_zones = autoscale_group.get_availability_zones(
                client=ec2_client
            )
        logger.info(f"using zones: {availability_zones}")
        logger.info("create autoscaling group")
        rd[
            "autoscale_group_context"
        ] = autoscale_group.create_autoscaling_group(
            client=auto_scale_client,
            name=rd["names"]["autoscale_group"],
            launch_template_context=rd["launch_template_context"],
            min_size=rd["min_virtual_cpu"] // 8,
            max_size=rd["max_virtual_cpu"] // 8,
            availability_zones=availability_zones,
            vpc_zone_identifier=vpc_zone_identifier,
        )

        return rd

    except ClientError as err:
        # from:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html

        if (
            "Error" in err.response
            and "Code" in err.response["Error"]
            and "Message" in err.response["Error"]
            and "ResponseMetadata" in err.response
        ):
            if (
                err.response["Error"]["Code"] == "InternalError"
            ):  # Generic error
                logger.error(
                    "Error Message: {}".format(
                        err.response["Error"]["Message"]
                    )
                )
                logger.error(
                    "Request ID: {}".format(
                        err.response["ResponseMetadata"]["RequestId"]
                    )
                )
                logger.error(
                    "Http code: {}".format(
                        err.response["ResponseMetadata"]["HTTPStatusCode"]
                    )
                )
            else:
                raise err
        else:
            raise err
    finally:
        _write_resources_file(rd, resource_description_path)
    return {}
