import os
import json

from argparse import ArgumentParser
from cbm3_aws import log_helper
from cbm3_aws.namespace import Namespace
from cbm3_aws.aws import execution


def main():
    parser = ArgumentParser(
        description="Starts an execution on a cbm3_aws cluster")

    parser.add_argument(
        "--resource_description_path", required=True, type=os.path.abspath,
        help="Path to a json formatted file containing the allocated AWS "
             "cbm3_aws cluster")
    parser.add_argument(
        "--execution_name", required=True,
        help="The name of the activity to create. This name must be unique "
             "for your AWS account and region for 90 days. For more "
             "information, see Limits Related to State Machine Executions "
             "in the AWS Step Functions Developer Guide.")
    parser.add_argument(
        "--tasks_path", required=True, type=os.path.abspath,
        help="Path to json formatted tasks who has at a minimum a "
             "'task_list' key whose value is the list of tasks to "
             "pass to each instance as it calls get_activity_task")

    log_helper.start_logging(level="INFO")
    logger = log_helper.get_logger()
    try:
        args = parser.parse_args()
        logger.info("start_execution")
        logger.info(vars(args))

        with open(args.resource_description_path, 'r') as resources_fp:
            rd = Namespace(**json.load(resources_fp))
        with open(args.tasks_path, 'r') as tasks_fp:
            tasks = json.load(tasks_fp)
        execution.start_execution(
            execution_name=args.execution_name,
            state_machine_arn=rd.state_machine_context.app_state_machine_arn,
            region_name=rd.region_name,
            tasks=tasks)

    except Exception:
        logger.exception("")


if __name__ == "__main__":
    main()
