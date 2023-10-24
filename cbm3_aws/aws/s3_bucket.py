from mypy_boto3_s3.client import S3Client
from mypy_boto3_s3.type_defs import CreateBucketConfigurationTypeDef
from mypy_boto3_s3.literals import BucketLocationConstraintType


def create_bucket(
    client: S3Client, bucket_name: str, region: BucketLocationConstraintType
):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    Args:
        client (S3Client): boto s3 client
        bucket_name (str): Bucket to create
        region (str): String region to create bucket in, e.g., 'us-west-2'.
    """
    location = CreateBucketConfigurationTypeDef(
        {"LocationConstraint": (region)}
    )
    client.create_bucket(
        Bucket=bucket_name, CreateBucketConfiguration=location
    )
