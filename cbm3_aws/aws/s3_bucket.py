def create_bucket(client, bucket_name, region):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    Args:
        bucket_name (str): Bucket to create
        region (str): String region to create bucket in, e.g., 'us-west-2'.
    """
    location = {"LocationConstraint": region}
    client.create_bucket(
        Bucket=bucket_name, CreateBucketConfiguration=location
    )
