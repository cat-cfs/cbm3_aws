from cbm3_python import toolbox_defaults
from cbm3_python.simulation import projectsimulator


class InstanceTask:

    def __init__(self, task_message, task, local_working_dir):
        pass

    @property
    def project_path(self):
        pass

    @property
    def simulation_id(self):
        pass

    @property
    def executable_path(self):
        pass

    @property
    def aidb_path(self):
        pass

    @property
    def results_database_path(self):
        pass

    @property
    def tempfiles_output_dir(self):
        pass

    @property
    def stdout_path(self):
        pass

    @property
    def dist_classes_path(self):
        pass

    @property
    def dist_rules_path(self):
        pass

    @property
    def results_dir(self):
        pass


def generate_instance_tasks(task_message, local_working_dir):
    yield InstanceTask()


def generate_run_args(instance_tasks):
    for task in instance_tasks:

        yield {
            "project_path": task.project_path,
            "project_simulation_id": task.simulation_id,
            "aidb_path": task.aidb_path,
            "cbm_exe_path": task.get_executable_path,
            "results_database_path": task.results_database_path,
            "tempfiles_output_dir": task.tempfiles_output_dir,
            "stdout_path": task.stdout_path,
            "copy_makelist_results": True,
            "dist_classes_path": task.dist_classes_path,
            "dist_rules_path": task.dist_rules_path
            }


def run_tasks(task_message, local_working_dir):
    instance_tasks = generate_instance_tasks(task_message)
    args_list = list(generate_run_args(instance_tasks))
    projectsimulator.run_concurrent(
        args_list, toolbox_defaults.INSTALL_PATH)
    for instance_task in instance_tasks:
        # todo: upload results dir to s3 key
        pass
