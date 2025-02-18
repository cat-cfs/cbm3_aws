from argparse import ArgumentParser
from cbm3_aws import log_helper
from cbm3_aws.instance import instance_task


def main():
    log_helper.start_logging("instance_process", level="INFO")
    logger = log_helper.get_logger("instance_process")
    logger.info("instance_process start up")

    parser = ArgumentParser(description="Run the cbm3_aws instance task")

    parser.add_argument(
        "--process_index",
        required=True,
        type=int,
        help="integer to identify this process on an instance",
    )
    parser.add_argument(
        "--activity_arn",
        required=True,
        help="Amazon Resource Name for a AWS step functions activity",
    )
    parser.add_argument(
        "--s3_bucket_name",
        required=True,
        help="Name of the s3 bucket that the instance will interact with",
    )
    parser.add_argument("--region_name", required=True, help="AWS region name")
    parser.add_argument(
        "--max_concurrency",
        required=True,
        type=int,
        help="Maximum number of concurrent sub processes to run in this "
        "instance",
    )

    try:
        args = parser.parse_args()
        logger.info(vars(args))

        instance_task.run(
            process_index=args.process_index,
            activity_arn=args.activity_arn,
            s3_bucket_name=args.s3_bucket_name,
            region_name=args.region_name,
            max_concurrency=args.max_concurrency,
        )
    except Exception:
        logger.exception("")


if __name__ == "__main__":
    main()
