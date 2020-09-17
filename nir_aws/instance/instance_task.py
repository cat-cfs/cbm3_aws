import os
from cbm3_python import toolbox_defaults
from cbm3_python.simulation import projectsimulator
from cbm3_python.simulation import toolbox_env


def make_resources_local(resources, working_dir):
    """clones the resources object and makes copies of each resource in the
    specified working_dir.

    Args:
        resources (object): the resources object containing shared instance
            resources.
        working_dir (str): path to the subprocess working dir into which to
            copy the shared resources

    Returns:
        object: a copy of the specified resources object cloned into the
            specified working dir.
    """
    pass


def run_tasks(tasks):
    pass


def run_task(task, resources, working_dir):

    local_resources = make_resources_local(resources, working_dir)
    toolbox_env_dir = os.path.join(working_dir, "toolbox_env")
    toolbox_env.create_toolbox_env(
        toolbox_defaults.INSTALL_PATH, toolbox_env_dir)

    temp_files_dir = os.path.join(working_dir, "temp_files")
    results_database_path = os.path.join(
        working_dir, f"{task.simulation_id}.mdb")

    projectsimulator.run(
        project_path=local_resources.projects[task.project_name],
        aidb_path=local_resources.aidb_path,
        toolbox_installation_dir=toolbox_env_dir,
        cbm_exe_path=local_resources.cbm_exe_path,
        tempfiles_output_dir=temp_files_dir,
        results_database_path=results_database_path,
        skip_makelist=False,
        use_existing_makelist_output=False,
        copy_makelist_results=True,
        stdout_path=os.path.join(temp_files_dir, "stdout.txt"),
        dist_classes_path=local_resources.dist_classes_path,
        dist_rules_path=local_resources.dist_rules_path,
        loader_settings=None)
