from types import SimpleNamespace
from cbm3_aws import constants
import json


def delete_role(client, role_context):
    """delete the role and policies based on the name/ARN specified in
     role_context"""
    pass


def create_state_machine_execution_policy(client, account_number):
    role_name = "cbm3_state_machine_role"
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

    create_policy_response = client.create_policy(
        PolicyName='cbm3_state_machine_policy',
        Path='/',
        PolicyDocument=json.dumps(policy),
        Description='grants access for state machine execution')

    create_role_response = client.create_role(
        Path='/',
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(states_assume_role_policy),
        Description='grants ec2 instances read and write permission to '
                    'specific bucket')

    client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=create_policy_response["Arn"])

    return SimpleNamespace(
        role_name=create_role_response["RoleName"],
        policy_arn=create_policy_response["Arn"])


def create_instance_iam_role(client, s3_bucket_name):
    role_name = "cbm3_instance_iam_role"
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
                    'specific bucket')

    client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=create_policy_response["Arn"])

    return SimpleNamespace(
        role_name=create_role_response["RoleName"],
        policy_arn=create_policy_response["Arn"])
