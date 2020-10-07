

def download_results_database(s3_interface, project_code, simulation_id,
                              local_file_path):
    s3_interface.download_compressed(
        "results", f"{project_code}_{simulation_id}", local_file_path)


def download_tempfiles(s3_interface, project_code, simulation_id,
                       local_tempfiles_dir):
    s3_interface.download_compressed(
        "results", f"{project_code}_tempfiles_{simulation_id}",
        local_tempfiles_dir)


def download_project_database(s3_interface, project_code, local_path):
    s3_interface.download_compressed("projects", project_code, local_path)


def download_resource(s3_interface, name, local_path):
    s3_interface.download_compressed("resources", name, local_path)
