

def build(instance_message, instance_resources_dir):
    """Creates a list of tasks for running local cbm tasks based
    on a dictionary formatted message passed to this instance.  Downloads S3
    resources configured in the queue message necessary for the local task to
    execute.

    Args:
        instance_message (dict): instance specific message for projects to run

        Example Input::

            build(
                instance_message={
                    "upload_key": "uc2021/results",
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
                })

    Returns:
        dict: dictionary containing instance-local resource paths and a list of
            task objects consumable by:
            :py:func:`nir_aws.instance.instance_task.run_tasks`

            Example Return Value (based on example input)::

                {
                    "upload_key": "uc2021/results",
                    "resources": [
                        {"name": "cbm_executables",
                         "path": "resources/cbm_executables"},
                        {"name": "archive_index_database",
                         "path": "resources/archive_index.mdb"},
                        {"name": "dist_classes",
                         "path": "resources/disturbance_classes.csv"},
                        {"name": "dist_rules_path",
                         "path": "resources/disturbance_rules.csv"}
                    ],
                    "projects": [
                        {"name": "AB",
                         "path": "resources/projects/AB/AB_NIR_UC.mdb"},
                        {"name": "BCB",
                         "path": "resources/projects/BCB/BCB_NIR_UC.mdb"}
                    ],
                    "tasks": [
                        {"project_name": "AB",
                         "simulation_id": 1},
                        {"project_name": "AB",
                         "simulation_id": 2},
                        {"project_name": "BCB",
                         "simulation_id": 21},
                        {"project_name": "BCB",
                         "simulation_id": 22}
                    ]
                }

    """
    return None
