import json


def get_state_machine(task_state_machine_arn, max_concurrency):
    return json.dumps({
        "Comment": "Task to launch CBM run task state machines",
        "StartAt": "map_tasks",
        "States": {
            "map_tasks": {
                "Type": "Map",
                "InputPath": "$.jobs",
                "ItemsPath": "$.jobs",
                "MaxConcurrency": max_concurrency,
                "Iterator": {
                    "StartAt": "launch_cbm_task",
                    "States": {
                        "launch_cbm_task": {
                            "Type": "Task",
                            "Resource": task_state_machine_arn,
                            "End": True
                        }
                    }
                },
                "End": True
            }
        }
    })
