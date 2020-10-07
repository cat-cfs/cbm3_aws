
def upload_resource(s3_interface, name, path):
    s3_interface.upload_compressed("resources", name, path)


def upload_project(s3_interface, project_code, path):
    s3_interface.upload_compressed("projects", project_code, path)


def upload_results_database(s3_interface, project_code, simulation_id, path):
    s3_interface.upload_compressed(
        "results", f"{project_code}_{simulation_id}", path)


def upload_tempfiles(s3_interface, project_code, simulation_id, path):
    s3_interface.upload_compressed(
        "results", f"{project_code}_tempfiles_{simulation_id}", path)
