import boto3
import tempfile
from cbm3_aws.s3_interface import S3Interface
from cbm3_aws.s3_io import S3IO
from cbm3_aws import log_helper

logger = log_helper.get_logger(__name__)


def upload(
    s3_bucket_name: str, execution_s3_key_prefix: str, manifest: list[dict]
):
    """uploads items in the specified manifest to the specified s3 bucket
    using the execution_s3_key_prefix to produce an S3 key specific to an
    execution name.

        Example::

            upload(
                s3_bucket_name="my-bucket-name",
                execution_s3_key_prefix="execution-id-123",
                manifest=[
                    {
                        local_path: my_project_dir/project_a.mdb,
                        s3_key="project",
                        "project_code": "project_a"
                    }
                ])

    Args:
        s3_bucket_name (str): name of the AWS s3 bucket to upload items to
        execution_s3_key_prefix (str): s3 key prefix used to make upload s3
            keys specific to to the execution.
        manifest (iterable): iterable of dicts with args to
            :py:func:`cbm3_aws.s3_io.S3IO.upload`

    """

    with tempfile.TemporaryDirectory() as temp_dir:
        s3_io = S3IO(
            execution_s3_key_prefix=execution_s3_key_prefix,
            s3_interface=S3Interface(
                s3_resource=boto3.resource("s3"),
                bucket_name=s3_bucket_name,
                local_temp_dir=temp_dir,
            ),
        )

        for item in manifest:
            logger.info(f"uploading {item}")
            s3_io.upload(**item)
