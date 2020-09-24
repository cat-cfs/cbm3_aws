from cbm3_aws import constants
import json


def create_state_machine_execution_policy(account_number):
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


def create_instance_iam_role(client, s3_bucket_name):
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

    client.create_role(
        Path='/',
        RoleName='cbm3_instance_iam_role',
        AssumeRolePolicyDocument=json.dumps(ec2_assume_role_policy),
        Description='grants ec2 instances read and write permission to '
                    'specific bucket',
        PermissionsBoundary='string',
        Tags=[
            {
                'Key': 'string',
                'Value': 'string'
            }
        ])
