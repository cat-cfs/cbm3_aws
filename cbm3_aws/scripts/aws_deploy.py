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
        "--min_instances", required=True, type=int,
        help="minimum number of instances to deploy")
    parser.add_argument(
        "--max_instances", required=True, type=int,
        help="maximum number of instances to deploy")
    parser.add_argument(
        "--image_ami_id", required=True,
        help="Amazon machine image id for launching instances")
    parser.add_argument(
        "--instance_type", required=True,
        help="the Amazon EC2 instance type to use (eg: 'a1.medium'")
    parser.add_argument(
        "--resource_description_path", required=True,
        help="path to a writeable filepath but not existing file path for "
             "recording information for the allocated AWS resources")

    log_helper.start_logging(level="INFO")
    logger = log_helper.get_logger()

    try:
        args = parser.parse_args()

        logger.info("aws_deploy start up")
        logger.info(vars(args))

        resources.deploy(
            region_name=args.region_name,
            s3_bucket_name=args.s3_bucket_name,
            min_instances=args.min_instances,
            max_instances=args.max_instances,
            image_ami_id=args.image_ami_id,
            instance_type=args.instance_type,
            resource_description_path=os.path.abspath(
                args.resource_description_path))
    except Exception:
        logger.exception("")


if __name__ == "__main__":
    main()
