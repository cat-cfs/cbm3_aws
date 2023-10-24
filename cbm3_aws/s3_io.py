class S3IO:
    def __init__(self, execution_s3_key_prefix, s3_interface):
        self.s3_interface = s3_interface
        self.execution_s3_key_prefix = execution_s3_key_prefix
        self._register_methods()

    def _create_key_name_prefix(self, key_token):
        return "/".join(["cbm3_aws", self.execution_s3_key_prefix, key_token])

    def _register_methods(self):
        self.doc_name_methods = {
            "results": lambda **kwargs: f'{kwargs["project_code"]}_{kwargs["simulation_id"]}',
            "tempfiles": lambda **kwargs: f'{kwargs["project_code"]}_{kwargs["simulation_id"]}',
            "project": lambda **kwargs: f'{kwargs["project_code"]}',
            "resource": lambda **kwargs: f'{kwargs["resource_name"]}',
        }

    def download(self, local_path, s3_key, **kwargs):
        self.s3_interface.download_compressed(
            key_name_prefix=self._create_key_name_prefix(s3_key),
            document_name=self.doc_name_methods[s3_key](**kwargs),
            local_path=local_path,
        )

    def upload(self, local_path, s3_key, **kwargs):
        self.s3_interface.upload_compressed(
            key_name_prefix=self._create_key_name_prefix(s3_key),
            document_name=self.doc_name_methods[s3_key](**kwargs),
            local_path=local_path,
        )
