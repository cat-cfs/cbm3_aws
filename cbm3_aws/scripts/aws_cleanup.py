import os
import json

from argparse import ArgumentParser
from cbm3_aws import log_helper
from cbm3_aws.aws import resources
from cbm3_aws.namespace import Namespace


def main():
    parser = ArgumentParser(
        description="Deallocates AWS resources that were allocated for "
                    "cbm3_aws runs")

    parser.add_argument(
        "--resource_description_path", required=True,
        help="Path to a json formatted file containing the allocated AWS "
             "resources to de-allocate with this script.")

    log_helper.start_logging(level="DEBUG")
    logger = log_helper.get_logger()
    try:
        args = parser.parse_args()
        logger.info("aws_cleanup start up")
        logger.info(vars(args))

        path = os.path.abspath(args.resource_description_path)
        with open(path, 'r') as fp:
            data = Namespace(**json.load(fp))
        resources.cleanup(resource_description=data)
    except Exception:
        logger.exception("")


if __name__ == "__main__":
    main()
