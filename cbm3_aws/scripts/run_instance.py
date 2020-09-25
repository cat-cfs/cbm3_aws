from argparse import ArgumentParser
from cbm3_aws import log_helper
from cbm3_aws.instance import instance_task


def main():
    log_helper.start_logging()
    logger = log_helper.get_logger()
    logger.info("start up")

    parser = ArgumentParser(
        description="Run the cbm3_aws instance task")

    parser.add_argument(
        "activity_arn",
        help="Amazon Resource Name for a AWS step functions activity")
    parser.add_argument(
        "s3_bucket_name",
        help="Name of the s3 bucket that the instance will interact with")

    args = parser.parse_args()
    logger.info(vars(args))

    instance_task.run(
        activity_arn=args.activity_arn, s3_bucket_name=args.s3_bucket_name)


if __name__ == "__main__":
    main()
