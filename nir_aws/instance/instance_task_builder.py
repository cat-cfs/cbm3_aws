

def build(sqs_queue_data):
    """Creates a list of tasks for running local uncertainty tasks based
    on a dictionary formatted message drawn from the SQS queue.  Downloads S3
    resources configured in the queue message necessary for the local task to
    execute.

    Args:
        sqs_queue_data (dict): message from SQS Queue

        Example::

            sqs_queue_data = {
                "resources": [
                    {"name": "archive_index_database",
                    "s3_key": "uncertainty2021/resources/archive_index"},
                    {"name": "cbm_executables",
                    "s3_key": "uncertainty2021/resources/cbm_executables"},
                    {"name": "stand_recovery_rules",
                    "s3_key": "uncertainty2021/resources/stand_recovery_rules"}
                ],
                "simulations": [
                    {"name": "AB",
                    "project_s3_key": "uncertainty2021/projects/AB",
                    "simulation_ids": [1, 2, 3, 4]}
                ]
            }

    Returns:
        list: list of task objects consumable by
            :py:func:`nir_aws.instance.instance_task.run_tasks`
    """
    return []
