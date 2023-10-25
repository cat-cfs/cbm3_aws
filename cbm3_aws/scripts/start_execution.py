import os
import json

from argparse import ArgumentParser
from cbm3_aws import log_helper
from cbm3_aws.aws import execution


def main():
    parser = ArgumentParser(
        description="Starts an execution on a cbm3_aws cluster"
    )

    parser.add_argument(
        "--resource_description_path",
        required=True,
        type=os.path.abspath,
        help="Path to a json formatted file containing the allocated AWS "
        "cbm3_aws cluster",
    )
    parser.add_argument(
        "--execution_name",
        required=True,
        help="The name of the execution. This name must be unique for your "
        "AWS account, region, and state machine for 90 days. For more "
        "information, see Limits Related to State Machine Executions in "
        "the AWS Step Functions Developer Guide.",
    )
    parser.add_argument(
        "--tasks_file_path",
        required=True,
        type=os.path.abspath,
        help="Path to json formatted tasks who has at a minimum a "
        "'task_list' key whose value is the list of tasks to "
        "pass to each instance as they call get_activity_task",
    )
    parser.add_argument(
        "--response_output_path",
        required=True,
        type=os.path.abspath,
        help="Path",
    )

    log_helper.start_logging("start_execution", level="INFO")
    logger = log_helper.get_logger("start_execution")
    try:
        args = parser.parse_args()
        logger.info("start_execution")
        logger.info(vars(args))

        if os.path.exists(args.response_output_path):
            # do not overwrite an existing file, which could potentially
            # contain useful information.
            raise ValueError(
                "specified response_output_path already exists: "
                f"'{args.response_output_path}'"
            )

        with open(args.response_output_path, "w") as out_file:
            with open(args.resource_description_path, "r") as resources_fp:
                rd = json.load(resources_fp)
            with open(args.tasks_file_path, "r") as tasks_fp:
                tasks = json.load(tasks_fp)
            state_machine_arn = rd["state_machine_context"][
                "app_state_machine_arn"
            ]
            start_execution_response = execution.start_execution(
                execution_name=args.execution_name,
                state_machine_arn=state_machine_arn,
                region_name=rd["region_name"],
                tasks=tasks,
            )
            logger.info(json.dumps(start_execution_response, indent=4))
            json.dump(start_execution_response, out_file)

    except Exception:
        logger.exception("")


if __name__ == "__main__":
    main()
