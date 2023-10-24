import os
from logging import Logger
from typing import Iterator
from cbm3_aws.s3_io import S3IO
from cbm3_python.simulation import projectsimulator


def run_tasks(
    simulation_tasks: list[dict],
    local_working_dir: str,
    s3_io: S3IO,
    logger: Logger,
    max_concurrency: int,
):
    """Runs a CBM3 project simulation task

        :: Example simulation_tasks

            simulation_tasks = [
                {"project_code": "AB",
                "simulation_ids": [1, 2]},
                {"project_code": "BCB",
                "simulation_ids": [21, 22]}
                ]

    Args:
        simulation_tasks (list): list of simulation tasks to run.
        local_working_dir (str): writeable directory for processing CBM
            simulation
        s3_io (cbm3_aws.s3_io.S3IO) object for managing cbm3_aws
            uploads and downloads for AWS S3
        logger (logging.Logger): logger for this EC2 instance
        max_concurrency (int): maximum number of concurrent CBM simulations
            spawned by this process
    """

    # download resources
    logger.info("download resources")
    toolbox_env_path = os.path.join(local_working_dir, "toolbox_env")
    s3_io.download(
        local_path=toolbox_env_path,
        s3_key="resource",
        resource_name="toolbox_env",
    )

    archive_index_path = os.path.join(local_working_dir, "archive_index.mdb")
    s3_io.download(
        local_path=archive_index_path,
        s3_key="resource",
        resource_name="archive_index_database",
    )

    cbm_executables_dir = os.path.join(local_working_dir, "cbm_executables")
    s3_io.download(
        local_path=cbm_executables_dir,
        s3_key="resource",
        resource_name="cbm_executables",
    )

    stand_recovery_rules_dir = os.path.join(
        local_working_dir, "stand_recovery_rules"
    )
    s3_io.download(
        local_path=stand_recovery_rules_dir,
        s3_key="resource",
        resource_name="stand_recovery_rules",
    )
    disturbance_rules_path = os.path.join(
        stand_recovery_rules_dir, "99a_disturbance_rules.csv"
    )
    disturbance_classes_path = os.path.join(
        stand_recovery_rules_dir, "99b_disturbance_classes.csv"
    )

    logger.info("download projects")
    # download projects
    local_project_dir = os.path.join(local_working_dir, "projects")
    if not os.path.exists(local_project_dir):
        os.makedirs(local_project_dir)
    required_projects = set([x["project_code"] for x in simulation_tasks])
    local_projects = {}
    for project_code in required_projects:
        local_project_path = os.path.join(
            local_project_dir, f"{project_code}.mdb"
        )
        s3_io.download(
            local_path=local_project_path,
            s3_key="project",
            project_code=project_code,
        )
        local_projects[project_code] = local_project_path

    local_results_dir = os.path.join(local_working_dir, "results")
    if not os.path.exists(local_results_dir):
        os.makedirs(local_results_dir)

    args_list = []

    tasks = list(
        iterate_tasks(simulation_tasks, local_projects, local_results_dir)
    )

    for task in tasks:
        os.makedirs(os.path.dirname(task["results_database_path"]))

        args_list.append(
            {
                "project_path": task["project_path"],
                "project_simulation_id": task["simulation_id"],
                "aidb_path": archive_index_path,
                "cbm_exe_path": cbm_executables_dir,
                "results_database_path": task["results_database_path"],
                "tempfiles_output_dir": task["tempfiles_output_dir"],
                "stdout_path": task["stdout_path"],
                "copy_makelist_results": True,
                "dist_classes_path": disturbance_classes_path,
                "dist_rules_path": disturbance_rules_path,
            }
        )

    logger.info("starting CBM3 simulations")
    logger.info(dict(tasks=args_list))
    # max_workers=1 here since this script is currently run as one of many
    # duplicate processes.  If we add further conncurrency here it will
    # make the worker too busy.
    list(
        projectsimulator.run_concurrent(
            args_list, toolbox_env_path, max_workers=max_concurrency
        )
    )
    logger.info("CBM3 simulations finished")

    logger.info("Upload results")
    for task in tasks:
        logger.info(
            dict(
                project_code=task["project_code"],
                simulation_id=task["simulation_id"],
            )
        )
        s3_io.upload(
            local_path=task["results_database_path"],
            s3_key="results",
            project_code=task["project_code"],
            simulation_id=task["simulation_id"],
        )
        # remove the project db so it wont be uploaded in the next step
        os.unlink(task["results_database_path"])
        # upload all other files and dirs where the project was loaded as
        # "tempfiles" This will include the run flat files, stdout file and
        # the run log.
        s3_io.upload(
            local_path=os.path.dirname(task["tempfiles_output_dir"]),
            s3_key="tempfiles",
            project_code=task["project_code"],
            simulation_id=task["simulation_id"],
        )
    logger.info("CBM3 tasks finished")


def iterate_tasks(
    task_message: list[dict], local_projects: dict, local_results_dir: str
) -> Iterator[dict]:
    for task in task_message:
        for simulation_id in task["simulation_ids"]:
            project_code = task["project_code"]
            yield dict(
                project_code=project_code,
                project_path=local_projects[project_code],
                simulation_id=simulation_id,
                results_database_path=os.path.join(
                    local_results_dir,
                    project_code,
                    str(simulation_id),
                    f"{simulation_id}.mdb",
                ),
                tempfiles_output_dir=os.path.join(
                    local_results_dir,
                    project_code,
                    str(simulation_id),
                    f"temp_files_{simulation_id}",
                ),
                stdout_path=os.path.join(
                    local_results_dir,
                    project_code,
                    str(simulation_id),
                    f"stdout_{simulation_id}.txt",
                ),
            )
