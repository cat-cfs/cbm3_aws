import json


def get_state_machine(task_state_machine_arn: str) -> str:
    return json.dumps(
        {
            "Comment": "Task to launch CBM run task state machines",
            "StartAt": "map_tasks",
            "States": {
                "map_tasks": {
                    "Type": "Map",
                    "ItemsPath": "$.task_list",
                    "Parameters": {"Input.$": "$$.Map.Item.Value"},
                    "Iterator": {
                        "StartAt": "launch_cbm_task",
                        "States": {
                            "launch_cbm_task": {
                                "Type": "Task",
                                "Resource": "arn:aws:states:::states:startExecution.sync",  # noqa E501
                                "Parameters": {
                                    "StateMachineArn": task_state_machine_arn,
                                    "Input": {
                                        "Input.$": "$.Input",
                                        "AWS_STEP_FUNCTIONS_STARTED_BY_EXECUTION_ID.$": "$$.Execution.Id",  # noqa E501
                                    },
                                },
                                "End": True,
                            }
                        },
                    },
                    "End": True,
                }
            },
        }
    )
