

class S3IO:

    def __init__(self, execution_s3_key_prefix, s3_interface):
        self.s3_interface = s3_interface
        self.execution_s3_key_prefix = execution_s3_key_prefix

    def download_results_database(self, project_code, simulation_id,
                                  local_file_path):
        self.s3_interface.download_compressed(
            key_name_prefix="results",
            document_name=f"{project_code}_{simulation_id}",
            local_path=local_file_path)

    def download_tempfiles(self, project_code, simulation_id,
                           local_tempfiles_dir):
        self.s3_interface.download_compressed(
            key_name_prefix="results",
            document_name=f"{project_code}_tempfiles_{simulation_id}",
            local_path=local_tempfiles_dir)

    def download_project_database(self, project_code, local_path):
        self.s3_interface.download_compressed(
            key_name_prefix="projects",
            document_name=project_code,
            local_path=local_path)

    def download_resource(self, name, local_path):
        self.s3_interface.download_compressed(
            key_name_prefix="resources",
            document_name=name,
            local_path=local_path)
