from cbm3_aws import constants


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
