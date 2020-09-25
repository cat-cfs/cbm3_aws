from types import SimpleNamespace
from cbm3_aws import constants
import json


def delete_role(client, role_context):
    """delete the role based on the role name/ARN specified in
    role_context

    Args:
        client ([type]): [description]
        role_context ([type]): [description]
    """
    pass


def delete_policy(client, policy_context):
    """delete the policy based on the policy ARN specified in
     policy_context

    Args:
        client ([type]): [description]
        policy_context ([type]): [description]
    """
    pass


def create_autoscaling_group_policy(client, account_number):
    resource_string = \
        "arn:aws:autoscaling:*:" \
        f"{account_number}:autoScalingGroup:*" \
        f":autoScalingGroupName/{constants.AUTOSCALE_GROUP_NAME}"

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "autoscaling:UpdateAutoScalingGroup"
                ],
                "Resource": resource_string
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": "autoscaling:DescribeAutoScalingGroups",
                "Resource": "*"
            }
        ]
    }
    create_policy_response = client.create_policy(
        PolicyName='cbm3_autoscale_update_policy',
        Path='/',
        PolicyDocument=json.dumps(policy),
        Description='grants access for updating app autoscale group')
    return SimpleNamespace(policy_arn=create_policy_response["Arn"])


def create_state_machine_policy(client, account_number):
    prefix = f"arn:aws:states:*:{account_number}"
    resource_arn_list = [
        f"{prefix}:activity:{constants.CBM_RUN_ACTIVITY_NAME}",
        f"{prefix}:stateMachine:{constants.CBM3_RUN_STATE_MACHINE_NAME}",
        f"{prefix}:execution:{constants.CBM3_RUN_STATE_MACHINE_NAME}:*"
        f"{prefix}:stateMachine:{constants.CBM3_RUN_TASK_STATE_MACHINE_NAME}",
        f"{prefix}:execution:{constants.CBM3_RUN_TASK_STATE_MACHINE_NAME}:*"
    ]

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "0",
                "Effect": "Allow",
                "Action": [
                    "states:SendTaskSuccess",
                    "states:ListStateMachines",
                    "states:SendTaskFailure",
                    "states:ListActivities",
                    "states:SendTaskHeartbeat"
                ],
                "Resource": "*"
            },
            {
                "Sid": "1",
                "Effect": "Allow",
                "Action": "states:*",
                "Resource": resource_arn_list
            }
        ]
    }
    create_policy_response = client.create_policy(
        PolicyName='cbm3_state_machine_policy',
        Path='/',
        PolicyDocument=json.dumps(policy),
        Description='grants access for state machine execution')
    return SimpleNamespace(policy_arn=create_policy_response["Arn"])


def create_s3_bucket_policy(client, s3_bucket_name):
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "0",
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject"
                ],
                "Resource": f"arn:aws:s3:::{s3_bucket_name}/*"
            }
        ]
    }

    create_policy_response = client.create_policy(
        PolicyName='cbm3_s3_instance_policy',
        Path='/',
        PolicyDocument=json.dumps(policy),
        Description='grants basic access to a particular s3 bucket for '
                    'IAM instance role')

    return SimpleNamespace(policy_arn=create_policy_response["Arn"])


def create_state_machine_role(client, policy_context_list):
    role_name = "cbm3_state_machine_role"
    states_assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "states.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    create_role_response = client.create_role(
        Path='/',
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(states_assume_role_policy),
        Description='grants ec2 instances read and write permission to '
                    'specific bucket')

    for policy_context in policy_context_list:
        client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_context.policy_arn)

    return SimpleNamespace(
        role_arn=create_role_response["Arn"],
        role_name=create_role_response["RoleName"])


def create_instance_iam_role(client, policy_context_list):
    role_name = "cbm3_instance_iam_role"

    ec2_assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    create_role_response = client.create_role(
        Path='/',
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(ec2_assume_role_policy),
        Description='grants ec2 instances read and write permission to '
                    'specific bucket, state machine access, and autoscale '
                    'group access')

    for policy_context in policy_context_list:
        client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_context.policy_arn)

    return SimpleNamespace(
        role_arn=create_role_response["Arn"],
        role_name=create_role_response["RoleName"])
