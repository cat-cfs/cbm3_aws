from typing import Union
import uuid
from mypy_boto3_ec2.client import EC2Client
from mypy_boto3_autoscaling import AutoScalingClient

# fix for issue in instance-overrides, this is the list
# of instance types that do not have support for the
# Windows OS.  This is to ensure the autoscaling group does
# not attempt to spin-up instance types that do not support
# windows OS.

# provided by AWS support staff using the following procedure:

# Using the EC2 console and filtering for 'OD Windows Pricing',
# we can identify any instance types that are unsupported, and
# include them in 'ExcludedInstanceTypes'
AWS_NON_WINDOWS_SUPPORTING_INSTANCE_TYPES = [
    "a1*.*",
    "c6*.*",
    "c7*.*",
    "dl1.24xlarge",
    "f1.*",
    "g5g.*",
    "hpc7g.*",
    "i4g.*",
    "im4gn.*",
    "inf*.*",
    "is4gen.*",
    "m6g*.*",
    "m7g*.*"
    "mac*.*",
    "p4d.24xlarge",
    "p5.48xlarge",
    "r6g*.*",
    "r7g*.*",
    "t4g*.*"
    "trn1*.*",
    "vt1.*",
    "x2gd.*"
]


def delete_launch_template(client: EC2Client, context: dict[str, str]):
    """Drop launch template associated with the specified context

    Args:
        client (EC2Client): boto3 ec2 client
        context (dict): context returned by:
            :py:func:`create_launch_template`
    """
    client.delete_launch_template(
        DryRun=False, LaunchTemplateId=context["launch_template_id"]
    )


def create_launch_template(
    client: EC2Client,
    name: str,
    image_ami_id: str,
    iam_instance_profile_arn: str,
    user_data: str,
) -> dict[str, str]:
    """Create a launch template for provisioning instances

    Args:
        client (EC2.Client): boto3 ec2 client
        name (str): the name of the launch template
        image_ami_id (str): the ami id for the launched instances
        iam_instance_profile_arn (str): ARN for for the Iam instance profile
            to attach to launched instances
        user_data (str): line break seperated commands to run on instance start

    Returns:
        object: launch template context object
    """
    client_token = str(uuid.uuid4())

    response = client.create_launch_template(
        DryRun=False,
        ClientToken=client_token,
        LaunchTemplateName=name,
        LaunchTemplateData={
            "EbsOptimized": False,
            "IamInstanceProfile": {
                "Arn": iam_instance_profile_arn,
            },
            "ImageId": image_ami_id,
            "Monitoring": {"Enabled": True},
            "InstanceInitiatedShutdownBehavior": "terminate",
            "UserData": user_data,
            "TagSpecifications": [
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": "CBM3 Worker Instance"},
                    ],
                },
                {
                    "ResourceType": "volume",
                    "Tags": [
                        {"Key": "Name", "Value": "CBM3 Worker volume"},
                    ],
                },
            ],
        },
        TagSpecifications=[
            {
                "ResourceType": "launch-template",
                "Tags": [
                    {"Key": "name", "Value": "CBM3 launch template"},
                ],
            },
        ],
    )

    launch_template = response["LaunchTemplate"]
    if (
        "LaunchTemplateName" not in launch_template
        or "LaunchTemplateId" not in launch_template
    ):
        raise ValueError(
            "error in create_launch_template response: missing name and id"
        )
    launch_template_name = launch_template["LaunchTemplateName"]
    launch_template_id = launch_template["LaunchTemplateId"]

    return dict(
        launch_template_name=launch_template_name,
        launch_template_id=launch_template_id,
    )


def get_availability_zones(client: EC2Client) -> list:
    """Gets the all availability zones that have at least one default subnet

    TODO: check if there a better way to handle this?

    Args:
        client (EC2Client): boto3 ec2 client

    Returns:
        list: list of strings naming the matching zones for the current region
    """
    describe_availability_zones_response = client.describe_availability_zones()
    zones = describe_availability_zones_response["AvailabilityZones"]

    available_zones = []
    for zone in zones:
        if "ZoneName" not in zone or "State" not in zone:
            raise ValueError(
                "error in describe_availability_zones response. "
                "Expected 'ZoneName' and 'State'."
            )
        if zone["State"] == "available":
            available_zones.append(zone["ZoneName"])

    describe_subnets_response = client.describe_subnets(
        Filters=[{"Name": "default-for-az", "Values": ["true"]}]
    )
    available_zones_with_subnet = []
    for subnet in describe_subnets_response["Subnets"]:
        if "AvailabilityZone" not in subnet:
            raise ValueError("AvailabilityZone not present in response")
        if subnet["AvailabilityZone"] in available_zones:
            available_zones_with_subnet.append(subnet["AvailabilityZone"])
    return available_zones_with_subnet


def create_autoscaling_group(
    client: AutoScalingClient,
    name: str,
    launch_template_context: dict,
    min_size: int,
    max_size: int,
    availability_zones: Union[list, None] = None,
    vpc_zone_identifier: Union[str, None] = None,
):
    """Create an autoscaling group to manage spot instances.

    Args:
        client (AutoScaling.Client): boto3 autoscaling client
        name (str): the name of the autoscaling group
        launch_template_context (object): Return value of:
            :py:func:`create_launch_template`
        min_size (int): minimum number of threads to run in auto scaling
            group.
        max_size (int): maximum number of threads to run in auto scaling
            group.
        availability_zones (list, Optional): the list of availability zones
            for the autoscaling group.
        vpc_zone_identifier (str, Optional): A comma-separated list of subnet
            IDs for your virtual private cloud (VPC).

    Returns:
        object: autoscaling group context
    """

    kwargs = dict(
        AutoScalingGroupName=name,
        MixedInstancesPolicy={
            "LaunchTemplate": {
                "LaunchTemplateSpecification": {
                    "LaunchTemplateId": launch_template_context[
                        "launch_template_id"
                    ]
                },
                "Overrides": [
                    {
                        "InstanceRequirements": {
                            "VCpuCount": {"Min": 8, "Max": 8},
                            "MemoryMiB": {"Min": 10000, "Max": 33000},
                            "CpuManufacturers": ["intel"],
                            "ExcludedInstanceTypes": AWS_NON_WINDOWS_SUPPORTING_INSTANCE_TYPES
                        },
                    },
                ],
            },
            "InstancesDistribution": {
                # prioritized by the order of the above overrides list
                # for on-demand only
                "OnDemandAllocationStrategy": "lowest-price",
                # minimum number of On demand instances
                "OnDemandBaseCapacity": 0,
                # percent of on demand versus spot instances
                "OnDemandPercentageAboveBaseCapacity": 0,
                "SpotAllocationStrategy": "price-capacity-optimized",
            },
        },
        MinSize=min_size,
        MaxSize=max_size,
        TerminationPolicies=["NewestInstance"],
        NewInstancesProtectedFromScaleIn=False,
    )

    if availability_zones:
        kwargs["AvailabilityZones"] = availability_zones
    if vpc_zone_identifier:
        kwargs["VPCZoneIdentifier"] = vpc_zone_identifier

    client.create_auto_scaling_group(**kwargs)

    return dict(auto_scaling_group_name=name)


def delete_autoscaling_group(
    client: AutoScalingClient, context: dict[str, str]
):
    """Delete an autoscaling group created by
        :py:func:`create_autoscaling_group`

    Args:
        client (AutoScaling.Client): boto3 autoscaling client
        context (object): context object returned by:
            :py:func:`create_autoscaling_group`
    """
    client.delete_auto_scaling_group(
        AutoScalingGroupName=context["auto_scaling_group_name"],
        ForceDelete=True,
    )
