import json
from cbm3_aws.namespace import Namespace


def delete_instance_profile(client, role_context):
    """Removes the AWS instance profile which is necessary before deleting the
    instance role.

    Args:
        client (IAM.client): boto3 IAM client
        role_context (namespace): object containing identifying information
            for the role and instance profile to delete.
    """
    client.remove_role_from_instance_profile(
        InstanceProfileName=role_context.instance_profile_name,
        RoleName=role_context.role_name,
    )

    client.delete_instance_profile(
        InstanceProfileName=role_context.instance_profile_name
    )


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
    list_entities_for_policy_response = client.list_entities_for_policy(
        PolicyArn=policy_context.policy_arn, EntityFilter="Role"
    )
    for role in list_entities_for_policy_response["PolicyRoles"]:
        client.detach_role_policy(
            RoleName=role["RoleName"], PolicyArn=policy_context.policy_arn
        )
    client.delete_policy(PolicyArn=policy_context.policy_arn)


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

    # see:
    # https://docs.aws.amazon.com/step-functions/latest/dg/stepfunctions-iam.html
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["states:StartExecution"],
                "Resource": [
                    f"arn:aws:states:*:{account_number}:stateMachine:*"
                ],
            },
            {
                "Effect": "Allow",
                "Action": ["states:DescribeExecution", "states:StopExecution"],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "events:PutTargets",
                    "events:PutRule",
                    "events:DescribeRule",
                ],
                "Resource": [
                    f"arn:aws:events:*:{account_number}:"
                    "rule/StepFunctionsGetEventsForStepFunctionsExecutionRule"
                ],
            },
        ],
    }
    create_policy_response = client.create_policy(
        PolicyName=names.state_machine_policy,
        Path="/",
        PolicyDocument=json.dumps(policy),
        Description="grants access for state machine execution",
    )
    return Namespace(policy_arn=create_policy_response["Policy"]["Arn"])


def create_ec2_worker_policy(client, s3_bucket_name, account_number, names):
    """Create a policy object for:
        1. permitting put/get/delete operations on the
           specified named bucket
        2. interact with activity tasks for the cbm3_aws state machine

    Args:
        client (IAM.client): boto3 IAM client
        s3_bucket_name (str): the name of the bucket for which to assign the
            policy
        names (namespace): the names used to label provisioned aws resources

    Returns:
        namespace: a namespace containing the policy ARN
    """
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "0",
                "Effect": "Allow",
                "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                "Resource": f"arn:aws:s3:::{s3_bucket_name}/*",
            },
            {
                "Sid": "1",
                "Effect": "Allow",
                "Action": "states:GetActivityTask",
                "Resource": f"arn:aws:states:*:{account_number}:activity:"
                f"{names.run_activity}",
            },
            {
                "Sid": "2",
                "Effect": "Allow",
                "Action": [
                    "states:SendTaskSuccess",
                    "states:SendTaskFailure",
                    "states:ListActivities",
                    "states:SendTaskHeartbeat",
                ],
                "Resource": "*",
            },
            {
                "Sid": "3",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogStream",
                    "logs:CreateLogGroup",
                    "logs:PutLogEvents",
                ],
                "Resource": [
                    f"arn:aws:logs:*:{account_number}:log-group:cbm3_aws",
                    f"arn:aws:logs:*:{account_number}:log-group:cbm3_aws:log-stream:*",
                ],
            },
        ],
    }

    create_policy_response = client.create_policy(
        PolicyName=names.instance_s3_policy,
        Path="/",
        PolicyDocument=json.dumps(policy),
        Description="grants read/write/delete access to a particular s3 "
        "bucket and step function activity tasks access for "
        "IAM instance role",
    )

    return Namespace(policy_arn=create_policy_response["Policy"]["Arn"])


def create_state_machine_role(client, policy_context_list, names):
    """Create an state machine IAM role

    Args:
        client (IAM.client): boto3 IAM client
        policy_context_list (list): list of objects containing the
            policy ARN to assign to the state machine IAM role.
        names (namespace): the names used to label provisioned aws resources

    Returns:
        namespace: context object containing the IAM role's identifying
            information
    """

    states_assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "states.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    create_role_response = client.create_role(
        Path="/",
        RoleName=names.state_machine_role,
        AssumeRolePolicyDocument=json.dumps(states_assume_role_policy),
        Description="grants ec2 instances read and write permission to "
        "specific bucket",
    )

    for policy_context in policy_context_list:
        client.attach_role_policy(
            RoleName=names.state_machine_role,
            PolicyArn=policy_context.policy_arn,
        )

    return Namespace(
        role_arn=create_role_response["Role"]["Arn"],
        role_name=create_role_response["Role"]["RoleName"],
    )


def create_instance_iam_role(client, policy_context_list, names):
    """Create an instance IAM role

    Args:
        client (IAM.client): boto3 IAM client
        policy_context_list (list): list of objects containing the
            policy ARN to assign to the instance IAM role.
        names (namespace): the names used to label provisioned aws resources

    Returns:
        namespace: context object containing the identifying
            information belonging to the IAM role and Instance profile
    """

    ec2_assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    create_role_response = client.create_role(
        Path="/",
        RoleName=names.instance_iam_role,
        AssumeRolePolicyDocument=json.dumps(ec2_assume_role_policy),
        Description="grants ec2 instances read and write permission to "
        "specific bucket, state machine access, and autoscale "
        "group access",
    )

    for policy_context in policy_context_list:
        client.attach_role_policy(
            RoleName=names.instance_iam_role,
            PolicyArn=policy_context.policy_arn,
        )

    create_instance_profile_response = client.create_instance_profile(
        InstanceProfileName=names.instance_iam_role
    )

    client.add_role_to_instance_profile(
        InstanceProfileName=names.instance_iam_role,
        RoleName=names.instance_iam_role,
    )

    return Namespace(
        role_arn=create_role_response["Role"]["Arn"],
        role_name=create_role_response["Role"]["RoleName"],
        instance_profile_name=create_instance_profile_response[
            "InstanceProfile"
        ]["InstanceProfileName"],
        instance_profile_id=create_instance_profile_response[
            "InstanceProfile"
        ]["InstanceProfileId"],
        instance_profile_arn=create_instance_profile_response[
            "InstanceProfile"
        ]["Arn"],
    )
