from argparse import ArgumentParser
from cbm3_aws import log_helper
from cbm3_aws.aws import app


def main():
    log_helper.start_logging()
    logger = log_helper.get_logger()
    logger.info("aws_deploy start up")

    app.start(
        region_name, s3_bucket_name, n_instances, image_ami_id,
        instance_type, tasks)