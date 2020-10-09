from argparse import ArgumentParser
from cbm3_aws import log_helper
from cbm3_aws.instance import instance_task


def main():
    log_helper.start_logging("run_instance", level="INFO")
    logger = log_helper.get_logger("run_instance")
    logger.info("run_instance start up")

    parser = ArgumentParser(
        description="Run the cbm3_aws instance task")

    parser.add_argument(
        "--activity_arn", required=True,
        help="Amazon Resource Name for a AWS step functions activity")
    parser.add_argument(
        "--s3_bucket_name", required=True,
        help="Name of the s3 bucket that the instance will interact with")
    parser.add_argument(
        "--region_name", required=True,
        help="AWS region name")

    try:
        args = parser.parse_args()
        logger.info(vars(args))

        instance_task.run(
            activity_arn=args.activity_arn, s3_bucket_name=args.s3_bucket_name,
            region=args.region_name)
    except Exception:
        logger.exception("")


if __name__ == "__main__":
    main()
