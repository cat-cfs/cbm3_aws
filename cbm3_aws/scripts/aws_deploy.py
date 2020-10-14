import os
from argparse import ArgumentParser
from cbm3_aws import log_helper
from cbm3_aws.aws import resources


def main():

    parser = ArgumentParser(
        description="Deploy a cbm3_aws cluster for processing CBM3 runs")

    parser.add_argument(
        "--region_name", required=True,
        help="The region name for deploying the cluster")
    parser.add_argument(
        "--s3_bucket_name", required=True,
        help="Name of the s3 bucket that the the application will interact"
             "with")
    parser.add_argument(
        "--min_virtual_cpu", required=True, type=int,
        help="minimum number of virtual CPUs to deploy")
    parser.add_argument(
        "--max_virtual_cpu", required=True, type=int,
        help="maximum number of virtual CPUs to deploy")
    parser.add_argument(
        "--image_ami_id", required=True,
        help="Amazon machine image id for launching instances")
    parser.add_argument(
        "--resource_description_path", required=True,
        help="path to a writeable filepath but not existing file path for "
             "recording information for the allocated AWS resources")

    log_helper.start_logging("aws_deploy", level="INFO")
    logger = log_helper.get_logger("aws_deploy")

    try:
        args = parser.parse_args()

        logger.info("aws_deploy start up")
        logger.info(vars(args))

        resources.deploy(
            region_name=args.region_name,
            s3_bucket_name=args.s3_bucket_name,
            min_virtual_cpu=args.min_virtual_cpu,
            max_virtual_cpu=args.max_virtual_cpu,
            image_ami_id=args.image_ami_id,
            resource_description_path=os.path.abspath(
                args.resource_description_path))
    except Exception:
        logger.exception("")


if __name__ == "__main__":
    main()
