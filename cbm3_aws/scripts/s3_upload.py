import os
import json

from argparse import ArgumentParser
from cbm3_aws import log_helper
from cbm3_aws.aws import s3_upload


def main():

    parser = ArgumentParser(
        description="Uploads files and dirs specified in manifest to AWS S3")

    parser.add_argument(
        "--s3_bucket_name", required=True,
        help="name of the existing AWS s3 bucket to upload items to")
    parser.add_argument(
        "--execution_s3_key_prefix", required=True,
        help="s3 key prefix used to make upload s3 keys specific to an "
             "execution.")
    parser.add_argument(
        "--manifest_path", required=True, type=os.path.abspath,
        help="path to a json formatted file describing local files to upload")

    log_helper.start_logging("s3_upload", level="INFO")
    logger = log_helper.get_logger("s3_upload")
    try:
        args = parser.parse_args()
        logger.info("start_uploads")
        logger.info(vars(args))

        with open(args.manifest_path) as manifest_file:
            manifest = json.load(manifest_file)
        s3_upload.upload(
            s3_bucket_name=args.s3_bucket_name,
            execution_s3_key_prefix=args.execution_s3_key_prefix,
            manifest=manifest)

    except Exception:
        logger.exception("")
