

def build(sqs_queue_data, instance_resources_dir):
    """Creates a list of tasks for running local uncertainty tasks based
    on a dictionary formatted message drawn from the SQS queue.  Downloads S3
    resources configured in the queue message necessary for the local task to
    execute.

    Args:
        sqs_queue_data (dict): message from SQS Queue

        Example Input::

            build(
                sqs_queue_data={
                    "resources": [
                        {"name": "archive_index_database",
                        "s3_key": "uc2021/resources/archive_index"},
                        {"name": "cbm_executables",
                        "s3_key": "uc2021/resources/cbm_executables"},
                        {"name": "stand_recovery_rules",
                        "s3_key": "uc2021/resources/stand_recovery_rules"}
                    ],
                    "simulations": [
                        {"name": "AB",
                        "s3_key": "uc2021/projects/AB",
                        "simulation_ids": [1, 2]},
                        {"name": "BCB",
                        "s3_key": "uc2021/projects/BCB",
                        "simulation_ids": [21, 22]},
                    ]
                }
                instance_resources_dir="/resources/")

    Returns:
        object: object containing resource paths and a list of task objects
            consumable by:
            :py:func:`nir_aws.instance.instance_task.run_tasks`

            Example Return Value (based on example input)::

                object(
                    resources=object(
                        cbm_exe_path="resources/cbm_executables",
                        aidb_path="resources/archive_index.mdb",
                        dist_classes_path="resources/disturbance_classes.csv",
                        dist_rules_path="resources/disturbance_rules.csv",
                        projects={
                            "AB": "resources/projects/AB/AB_NIR_UC.mdb",
                            "BCB": "resources/projects/BCB/BCB_NIR_UC.mdb"
                        }
                    ),
                    tasks=[
                        object(
                            project_name="AB",
                            simulation_id=1
                        ),
                        object(
                            project_name="AB",
                            simulation_id=2
                        ),
                        object(
                            project_name="BCB",
                            simulation_id=21
                        ),
                        object(
                            project_name="BCB",
                            simulation_id=22
                        )
                    ]
                )

    """
    return []
