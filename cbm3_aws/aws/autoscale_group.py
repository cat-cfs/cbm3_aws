import uuid
from cbm3_aws.namespace import Namespace


def delete_launch_template(client, context):
    """Drop launch template associated with the specified context

    Args:
        client (EC2.Client): boto3 ec2 client
        context (object): context object returned by:
            :py:func:`create_launch_template`
    """
    client.delete_launch_template(
        DryRun=False,
        LaunchTemplateId=context.launch_template_id)


def create_launch_template(client, name, image_ami_id, instance_type,
                           iam_instance_profile_arn, user_data):
    """Create a launch template for provisioning instances

    Args:
        client (EC2.Client): boto3 ec2 client
        name (str): the name of the launch template
        image_ami_id (str): the ami id for the launched instances
        instance_type (str): the type of the instance to launch
            (ex. 't1.micro')
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
            'EbsOptimized': False,
            'IamInstanceProfile': {
                'Arn': iam_instance_profile_arn,
            },
            'ImageId': image_ami_id,
            'InstanceType': instance_type,
            'Monitoring': {
                'Enabled': True
            },
            'InstanceInitiatedShutdownBehavior': 'terminate',
            'UserData': user_data,
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'CBM3 Worker Instance'
                        },
                    ]
                },
                {
                    'ResourceType': 'volume',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'CBM3 Worker volume'
                        },
                    ]
                },
            ],
            'InstanceMarketOptions': {
                'MarketType': 'spot',
                'SpotOptions': {
                    # 'MaxPrice': 'string', # up to the default on-demand price
                    'SpotInstanceType': 'one-time',
                    'InstanceInterruptionBehavior': 'terminate'
                }
            }
        },
        TagSpecifications=[
            {
                'ResourceType': 'launch-template',
                'Tags': [
                    {
                        'Key': 'name',
                        'Value': 'CBM3 launch template'
                    },
                ]
            },
        ]
    )

    return Namespace(
        launch_template_name=response["LaunchTemplate"]["LaunchTemplateName"],
        launch_template_id=response["LaunchTemplate"]["LaunchTemplateId"])


def get_availability_zones(client):
    """Gets the the first availability zone.

    TODO: check if there a better way to handle this?

    Args:
        client (EC2.Client): boto3 ec2 client

    Returns:
        list: list of strings naming the matching zones for the current region
    """
    describe_availability_zones_response = client.describe_availability_zones()
    zones = describe_availability_zones_response["AvailabilityZones"]
    available_zones = [
        zone["ZoneName"] for zone in zones if zone["State"] == "available"]
    return [available_zones[0]]


def create_autoscaling_group(client, name, launch_template_context, min_size,
                             max_size, availability_zones):
    """Create an autoscaling group to manage spot instances.

    Args:
        client (AutoScaling.Client): boto3 autoscaling client
        name (str): the name of the autoscaling group
        launch_template_context (object): Return value of:
            :py:func:`create_launch_template`
        min_size (int): minimum number of instances to run in auto scaling
            group.
        max_size (int): maximum number of instances to run in auto scaling
            group.
        availability_zones (list): the list of availability zones for the
            autoscaling group.

    Returns:
        object: autoscaling group context
    """
    client.create_auto_scaling_group(
        AutoScalingGroupName=name,
        LaunchTemplate={
            'LaunchTemplateId': launch_template_context.launch_template_id,
        },
        MinSize=min_size,
        MaxSize=max_size,
        TerminationPolicies=["NewestInstance"],
        NewInstancesProtectedFromScaleIn=False,
        AvailabilityZones=availability_zones
    )
    return Namespace(
        auto_scaling_group_name=name)


def delete_autoscaling_group(client, context):
    """Delete an autoscaling group created by
        :py:func:`create_autoscaling_group`

    Args:
        client (AutoScaling.Client): boto3 autoscaling client
        context (object): context object returned by:
            :py:func:`create_autoscaling_group`
    """
    client.delete_auto_scaling_group(
        AutoScalingGroupName=context.auto_scaling_group_name,
        ForceDelete=True)
