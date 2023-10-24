import json


def get_state_machine(cbm_run_task_activity_arn):
    return json.dumps(
        {
            "Comment": "Task to launch CBM runs and retry if they experience a "
            "spot interruption",
            "StartAt": "RunCBMTask",
            "States": {
                "RunCBMTask": {
                    "Comment": "starts the CBM run task activity",
                    "Type": "Task",
                    "Resource": cbm_run_task_activity_arn,
                    "HeartbeatSeconds": 60,
                    "Next": "StopCBMTask",
                    "Catch": [
                        {
                            "ErrorEquals": ["States.Timeout"],
                            "ResultPath": None,
                            "Next": "DelayThenRestart",
                        }
                    ],
                },
                "DelayThenRestart": {
                    "Type": "Wait",
                    "Seconds": 60,
                    "Next": "RunCBMTask",
                },
                "StopCBMTask": {"Type": "Succeed"},
            },
        }
    )
