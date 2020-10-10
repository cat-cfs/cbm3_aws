import json


def get_state_machine(task_state_machine_arn, max_concurrency):
    return json.dumps({
        "Comment": "Task to launch CBM run task state machines",
        "StartAt": "map_tasks",
        "States": {
            "map_tasks": {
                "Type": "Map",
                "ItemsPath": "$.task_list",
                "MaxConcurrency": int(max_concurrency),
                "Parameters": {
                    "Input.$": "$$.Map.Item.Value"
                },
                "Iterator": {
                    "StartAt": "launch_cbm_task",
                    "States": {
                        "launch_cbm_task": {
                            "Type": "Task",
                            "Resource": "arn:aws:states:::states:startExecution.sync",
                            "Parameters": {
                                "StateMachineArn": task_state_machine_arn,
                                "Input": {
                                    "Input.$": "$$.Input",
                                    "AWS_STEP_FUNCTIONS_STARTED_BY_EXECUTION_ID.$": "$$.Execution.Id"
                                }
                            },
                            "End": True
                        }
                    }
                },
                "End": True
            }
        }
    })
