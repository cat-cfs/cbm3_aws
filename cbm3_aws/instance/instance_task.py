import os
from types import SimpleNamespace
from cbm3_python import toolbox_defaults
from cbm3_python.simulation import projectsimulator

from cbm3_aws import download
from cbm3_aws import upload


def run_tasks(task_message, local_working_dir, s3_interface):
    """
        task_message = [
            {"project_code": "AB",
             "simulation_ids": [1, 2]},
            {"project_code": "BCB",
             "simulation_ids": [21, 22]}
            ]

    Args:
        task_message (list): list of simulation tasks
        local_working_dir ([type]): [description]
    """

    # download resources
    archive_index_path = os.path.join(
        local_working_dir, "archive_index.mdb")
    download.download_resources(
        s3_interface, "archive_index_database", archive_index_path)

    cbm_executables_dir = os.path.join(
        local_working_dir, "cbm_executables")
    download.download_resources(
        s3_interface, "cbm_executables", cbm_executables_dir)

    stand_recovery_rules_dir = os.path.join(
        local_working_dir, "stand_recovery_rules")
    download.download_resources(
        s3_interface, "stand_recovery_rules", stand_recovery_rules_dir)
    disturbance_rules_path = os.path.join(
        stand_recovery_rules_dir, "disturbance_rules.csv")
    disturbance_classes_path = os.path.join(
        stand_recovery_rules_dir, "disturbance_classes.csv")

    # download projects
    local_project_dir = os.path.join(local_working_dir, "projects")
    if not os.path.exists(local_project_dir):
        os.makedirs(local_project_dir)
    required_projects = set([x["project_code"] for x in task_message])
    local_projects = {}
    for project_code in required_projects:
        local_project_path = os.path.join(
            local_project_dir, f"{project_code}.mdb")
        download.download_project_database(
            s3_interface, project_code, local_project_path)
        local_projects[project_code] = local_project_path

    local_results_dir = os.path.join(local_working_dir, "results")
    if not os.path.exists(local_results_dir):
        os.makedirs(local_results_dir)

    args_list = []

    for task in iterate_tasks(task_message):

        args_list = [{
            "project_path": task.project_path,
            "project_simulation_id": task.simulation_id,
            "aidb_path": archive_index_path,
            "cbm_exe_path": cbm_executables_dir,
            "results_database_path": task.results_database_path,
            "tempfiles_output_dir": task.tempfiles_output_dir,
            "stdout_path": task.stdout_path,
            "copy_makelist_results": True,
            "dist_classes_path": disturbance_classes_path,
            "dist_rules_path": disturbance_rules_path
        }]

    projectsimulator.run_concurrent(
        args_list, toolbox_defaults.INSTALL_PATH)

    for task in iterate_tasks(task_message):
        upload.upload_results_database(
            s3_interface, task.project_code, task.simulation_id,
            task.results_database_path)
        upload.upload_tempfiles(
            s3_interface, task.project_code, task.simulation_id,
            task.tempfiles_output_dir)


def iterate_tasks(task_message, local_projects, local_results_dir):
    for task in task_message:
        for simulation_id in task["simulation_ids"]:
            project_code = task["project_code"]
            yield SimpleNamespace(
                project_code=project_code,
                project_path=local_projects[project_code],
                simulation_id=simulation_id,
                results_database_path=os.path.join(
                    local_results_dir,
                    project_code,
                    f"{simulation_id}.mdb"),
                tempfiles_output_dir=os.path.join(
                    local_results_dir,
                    project_code,
                    f"temp_files_{simulation_id}"),
                stdout_path=os.path.join(
                    local_results_dir,
                    project_code,
                    f"temp_files_{simulation_id}",
                    "stdout.txt")
                )
