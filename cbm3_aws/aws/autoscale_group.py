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
    "a1.medium",
    "a1.large",
    "a1.xlarge",
    "a1.2xlarge",
    "a1.4xlarge",
    "a1.metal",
    "c6g.medium",
    "c6g.large",
    "c6g.xlarge",
    "c6g.2xlarge",
    "c6g.4xlarge",
    "c6g.8xlarge",
    "c6g.12xlarge",
    "c6g.16xlarge",
    "c6g.metal",
    "c6gd.medium",
    "c6gd.large",
    "c6gd.xlarge",
    "c6gd.2xlarge",
    "c6gd.4xlarge",
    "c6gd.8xlarge",
    "c6gd.12xlarge",
    "c6gd.16xlarge",
    "c6gd.metal",
    "c6gn.medium",
    "c6gn.large",
    "c6gn.xlarge",
    "c6gn.2xlarge",
    "c6gn.4xlarge",
    "c6gn.8xlarge",
    "c6gn.12xlarge",
    "c6gn.16xlarge",
    "c7g.medium",
    "c7g.large",
    "c7g.xlarge",
    "c7g.2xlarge",
    "c7g.4xlarge",
    "c7g.8xlarge",
    "c7g.12xlarge",
    "c7g.16xlarge",
    "c7g.metal",
    "c7gd.medium",
    "c7gd.large",
    "c7gd.xlarge",
    "c7gd.2xlarge",
    "c7gd.4xlarge",
    "c7gd.8xlarge",
    "c7gd.12xlarge",
    "c7gd.16xlarge",
    "c7gn.medium",
    "c7gn.large",
    "c7gn.xlarge",
    "c7gn.2xlarge",
    "c7gn.4xlarge",
    "c7gn.8xlarge",
    "c7gn.12xlarge",
    "c7gn.16xlarge",
    "dl1.24xlarge",
    "f1.2xlarge",
    "f1.4xlarge",
    "f1.16xlarge",
    "g5g.xlarge",
    "g5g.2xlarge",
    "g5g.4xlarge",
    "g5g.8xlarge",
    "g5g.16xlarge",
    "g5g.metal",
    "hpc7g.4xlarge",
    "hpc7g.8xlarge",
    "hpc7g.16xlarge",
    "i4g.large",
    "i4g.xlarge",
    "i4g.2xlarge",
    "i4g.4xlarge",
    "i4g.8xlarge",
    "i4g.16xlarge",
    "im4gn.large",
    "im4gn.xlarge",
    "im4gn.2xlarge",
    "im4gn.4xlarge",
    "im4gn.8xlarge",
    "im4gn.16xlarge",
    "inf1.xlarge",
    "inf1.2xlarge",
    "inf1.6xlarge",
    "inf1.24xlarge",
    "inf2.xlarge",
    "inf2.8xlarge",
    "inf2.24xlarge",
    "inf2.48xlarge",
    "is4gen.medium",
    "is4gen.large",
    "is4gen.xlarge",
    "is4gen.2xlarge",
    "is4gen.4xlarge",
    "is4gen.8xlarge",
    "m6g.medium",
    "m6g.large",
    "m6g.xlarge",
    "m6g.2xlarge",
    "m6g.4xlarge",
    "m6g.8xlarge",
    "m6g.12xlarge",
    "m6g.16xlarge",
    "m6g.metal",
    "m6gd.medium",
    "m6gd.large",
    "m6gd.xlarge",
    "m6gd.2xlarge",
    "m6gd.4xlarge",
    "m6gd.8xlarge",
    "m6gd.12xlarge",
    "m6gd.16xlarge",
    "m6gd.metal",
    "m7g.medium",
    "m7g.large",
    "m7g.xlarge",
    "m7g.2xlarge",
    "m7g.4xlarge",
    "m7g.8xlarge",
    "m7g.12xlarge",
    "m7g.16xlarge",
    "m7g.metal",
    "m7gd.medium",
    "m7gd.large",
    "m7gd.xlarge",
    "m7gd.2xlarge",
    "m7gd.4xlarge",
    "m7gd.8xlarge",
    "m7gd.12xlarge",
    "m7gd.16xlarge",
    "mac1.metal",
    "mac2.metal",
    "mac2-m2.metal",
    "p4d.24xlarge",
    "p5.48xlarge",
    "r6g.medium",
    "r6g.large",
    "r6g.xlarge",
    "r6g.2xlarge",
    "r6g.4xlarge",
    "r6g.8xlarge",
    "r6g.12xlarge",
    "r6g.16xlarge",
    "r6g.metal",
    "r6gd.medium",
    "r6gd.large",
    "r6gd.xlarge",
    "r6gd.2xlarge",
    "r6gd.4xlarge",
    "r6gd.8xlarge",
    "r6gd.12xlarge",
    "r6gd.16xlarge",
    "r6gd.metal",
    "r7g.medium",
    "r7g.large",
    "r7g.xlarge",
    "r7g.2xlarge",
    "r7g.4xlarge",
    "r7g.8xlarge",
    "r7g.12xlarge",
    "r7g.16xlarge",
    "r7g.metal",
    "r7gd.medium",
    "r7gd.large",
    "r7gd.xlarge",
    "r7gd.2xlarge",
    "r7gd.4xlarge",
    "r7gd.8xlarge",
    "r7gd.12xlarge",
    "r7gd.16xlarge",
    "t4g.nano",
    "t4g.micro",
    "t4g.small",
    "t4g.medium",
    "t4g.large",
    "t4g.xlarge",
    "t4g.2xlarge",
    "trn1.2xlarge",
    "trn1.32xlarge",
    "trn1n.32xlarge",
    "vt1.3xlarge",
    "vt1.6xlarge",
    "vt1.24xlarge",
    "x2gd.medium",
    "x2gd.large",
    "x2gd.xlarge",
    "x2gd.2xlarge",
    "x2gd.4xlarge",
    "x2gd.8xlarge",
    "x2gd.12xlarge",
    "x2gd.16xlarge",
    "x2gd.metal",
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
