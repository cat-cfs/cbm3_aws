import json
from cbm3_aws.namespace import Namespace


def delete_role(client, role_context):
    """delete the role based on the role name/ARN specified in
    role_context

    Args:
        client (IAM.client): boto3 IAM client
        role_context (namespace): object containing identifying information
            for the role to delete.
    """
    client.delete_role(RoleName=role_context.role_name)


def delete_policy(client, policy_context):
    """delete the policy based on the policy ARN specified in
     policy_context

    Args:
        client (IAM.client): boto3 IAM client
        policy_context (namespace): object containing the ARN for the policy
            to delete.
    """
    client.delete_policy(
        PolicyArn=policy_context.policy_arn)


def create_autoscaling_group_policy(client, account_number, names):
    """Create policy to allow updating autoscale group

    Args:
        client (IAM.client): boto3 IAM client
        account_number (str): the AWS account number for filtering permitted
            resources
        names (namespace): the names used to label provisioned aws resources

    Returns:
        namespace: object containing the policy ARN
    """
    resource_string = \
        "arn:aws:autoscaling:*:" \
        f"{account_number}:autoScalingGroup:*" \
        f":autoScalingGroupName/{names.autoscale_group}"

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
    return Namespace(policy_arn=create_policy_response["Arn"])


def create_state_machine_policy(client, account_number, names):
    """Create a state machine policy to allow state machine function

    Args:
        client (IAM.client): boto3 IAM client
        account_number (str): the AWS account number for filtering permitted
            resources
        names (namespace): the names used to label provisioned aws resources

    Returns:
        namespace: object containing the policy ARN
    """
    prefix = f"arn:aws:states:*:{account_number}"
    resource_arn_list = [
        f"{prefix}:activity:{names.run_activity}",
        f"{prefix}:stateMachine:{names.run_state_machine}",
        f"{prefix}:execution:{names.run_task_state_machine}:*",
        f"{prefix}:stateMachine:{names.run_state_machine}",
        f"{prefix}:execution:{names.run_task_state_machine}:*"
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
    return Namespace(policy_arn=create_policy_response["Arn"])


def create_s3_bucket_policy(client, s3_bucket_name):
    """Create a policy object for permitting put/get/delete operations on the
    specified named bucket

    Args:
        client (IAM.client): boto3 IAM client
        s3_bucket_name (str): the name of the bucket for which to assign the
            policy

    Returns:
        namespace: a namespace containing the policy ARN
    """
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

    return Namespace(policy_arn=create_policy_response["Arn"])


def create_state_machine_role(client, policy_context_list):
    """Create an state machine IAM role

    Args:
        client (IAM.client): boto3 IAM client
        policy_context_list (list): list of objects containing the
            policy ARN to assign to the state machine IAM role.

    Returns:
        namespace: context object containing the IAM role's identifying
            information
    """
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

    return Namespace(
        role_arn=create_role_response["Arn"],
        role_name=create_role_response["RoleName"])


def create_instance_iam_role(client, policy_context_list):
    """Create an instance IAM role

    Args:
        client (IAM.client): boto3 IAM client
        policy_context_list (list): list of objects containing the
            policy ARN to assign to the instance IAM role.

    Returns:
        namespace: context object containing the IAM role's identifying
            information
    """
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

    return Namespace(
        role_arn=create_role_response["Arn"],
        role_name=create_role_response["RoleName"])
