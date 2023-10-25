import os
import json
import time
import tempfile
import traceback
from typing import Callable
import logging
from threading import Thread
from threading import Event
import boto3
import watchtower
from ec2_metadata import ec2_metadata
from botocore.client import Config
from cbm3_aws.instance import instance_cbm3_task
from cbm3_aws.s3_interface import S3Interface
from cbm3_aws.s3_io import S3IO
from mypy_boto3_stepfunctions.type_defs import GetActivityTaskOutputTypeDef


class HeartBeatThread(Thread):
    def __init__(self, event: Event, interval: int, target_func: Callable):
        Thread.__init__(self)
        self.stopped = event
        self.interval = interval
        self.target_func = target_func

    def run(self) -> None:
        while not self.stopped.wait(self.interval):
            self.target_func()


def _valid_token(
    get_activity_task_response: GetActivityTaskOutputTypeDef,
) -> bool:
    return (
        "taskToken" in get_activity_task_response
        and len(get_activity_task_response["taskToken"]) > 0
    )


def run(
    process_index: int,
    activity_arn: str,
    s3_bucket_name: str,
    region_name: str,
    max_concurrency: int,
) -> None:
    """Run a worker persistently on a single thread.

    The worker will call get_activity_task repeatedly with delayed retries
    until it gets a response from the cbm3_aws state machine.


        ::task input format (the content of activity_task_response["input"])

            "upload_s3_key": "string",
            "simulations":[
                {"project_code": "string", "simulation_ids": [integer]}
            ]

    Args:
        process_index (int): uniquely identifies the process for logging
        activity_arn (str): the resource name for the activity task to poll
        s3_bucket_name (str): the name of the s3 bucket to get input data
            from and to upload results to
        region_name (str): AWS region name
        max_concurrency (int): the maximum number of sub processes this
            process will spawn
    """

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("cbm3_aws.instance.instance_task")
    boto3_session = boto3.session.Session(region_name=region_name)
    instance_id = ec2_metadata.instance_id
    cloud_watch_log_handler = watchtower.CloudWatchLogHandler(
        log_group="cbm3_aws",
        stream_name=f"{instance_id}/process{process_index}",
        boto3_session=boto3_session,
    )
    logger.addHandler(cloud_watch_log_handler)

    # config here is based on the AWS recommendation found in the boto
    # docs, and the pull request here:
    # https://github.com/boto/botocore/pull/634
    client = boto3.client(
        "stepfunctions",
        region_name=region_name,
        config=Config(connect_timeout=65, read_timeout=65),
    )

    try:
        while True:
            logger.info("get_activity_task")
            get_activity_task_response = client.get_activity_task(
                activityArn=activity_arn
            )

            retry_interval = 30
            if not _valid_token(get_activity_task_response):
                time.sleep(retry_interval)
                logger.info("no activity task, retrying")
                # If there is a null task token it means there is no task
                # available. Sleep the worker and try again
                while not _valid_token(get_activity_task_response):
                    get_activity_task_response = client.get_activity_task(
                        activityArn=activity_arn
                    )
                    time.sleep(retry_interval)
                    logger.info("no activity task, retrying")

            task_token = get_activity_task_response["taskToken"]
            logger.info(f"got activity task, task_token {task_token}")
            task_input = json.loads(get_activity_task_response["input"])
            logger.info(dict(input=task_input))
            process_task(
                client=client,
                task_token=task_token,
                task_input=task_input["Input"],
                s3_bucket_name=s3_bucket_name,
                logger=logger,
                max_concurrency=max_concurrency,
            )

    except Exception:
        logger.exception("")


def get_heart_beat_func(client, task_token, logger):
    def hear_beat():
        logger.info("heartbeat")
        client.send_task_heartbeat(taskToken=task_token)

    return hear_beat


def process_task(
    client, task_token, task_input, s3_bucket_name, logger, max_concurrency
):
    heart_beat_stop_flag = Event()
    try:
        heart_beat_thread = HeartBeatThread(
            heart_beat_stop_flag,
            25,
            target_func=get_heart_beat_func(client, task_token, logger),
        )
        heart_beat_thread.start()

        with tempfile.TemporaryDirectory() as temp_dir:
            s3_working_dir = os.path.join(temp_dir, "s3_working")
            os.makedirs(s3_working_dir)

            s3_io = S3IO(
                execution_s3_key_prefix=task_input["upload_s3_key"],
                s3_interface=S3Interface(
                    s3_resource=boto3.resource("s3"),
                    bucket_name=s3_bucket_name,
                    local_temp_dir=s3_working_dir,
                ),
            )

            cbm3_working_dir = os.path.join(temp_dir, "cbm3_working")
            os.makedirs(cbm3_working_dir)
            logger.info("starting simulations")
            instance_cbm3_task.run_tasks(
                simulation_tasks=task_input["simulations"],
                local_working_dir=cbm3_working_dir,
                s3_io=s3_io,
                logger=logger,
                max_concurrency=max_concurrency,
            )

        client.send_task_success(
            taskToken=task_token,
            output=json.dumps(
                {
                    "output": {
                        "simulations": task_input["simulations"],
                        "errors": None,
                    }
                }
            ),
        )
    except Exception:
        # need to send task_success here to avoid interrupting the entire
        # state machine
        client.send_task_success(
            taskToken=task_token,
            output=json.dumps(
                {
                    "output": {
                        "simulations": task_input["simulations"],
                        "errors": traceback.format_exc(),
                    }
                }
            ),
        )
        heart_beat_stop_flag.set()
        time.sleep(60)
    finally:
        if not heart_beat_stop_flag.is_set():
            heart_beat_stop_flag.set()
