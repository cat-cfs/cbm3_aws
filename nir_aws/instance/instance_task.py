from cbm3_python


def run_tasks(tasks):
    pass


def run_task(task):

    with tempfile.TemporaryDirectory() as toolbox_env_dir:
        toolbox_env.create_toolbox_env(
            toolbox_defaults.INSTALL_PATH, toolbox_env_dir)

        projectsimulator.run(
            project_path=task.project_path,
            aidb_path=task.aidb_path,
            toolbox_installation_dir=toolbox_environment_path,
            cbm_exe_path=os.path.join(toolbox_environment_path, "admin", "executables"),
            results_database_path=os.path.abspath(".\\test_run\\Tutorial3_output.mdb"),
            tempfiles_output_dir=os.path.abspath(".\\test_run\\tempfiles"),
            skip_makelist=False,
            use_existing_makelist_output=False,
            copy_makelist_results=False,
            stdout_path=None,
            dist_classes_path=None,
            dist_rules_path=None,
            loader_settings=None)
