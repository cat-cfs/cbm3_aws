import os
import json
import time
import tempfile
import traceback
import psutil
from threading import Thread, Event
from concurrent.futures import ProcessPoolExecutor
import boto3
from botocore.client import Config
from cbm3_aws.instance import instance_cbm3_task
from cbm3_aws.s3_interface import S3Interface
from cbm3_aws.s3_io import S3IO


class HeartBeatThread(Thread):
    def __init__(self, event, interval, target_func):
        Thread.__init__(self)
        self.stopped = event
        self.interval = interval
        self.target_func = target_func

    def run(self):
        while not self.stopped.wait(self.interval):
            self.target_func()


def __valid_token(get_activity_task_response):
    return \
        "taskToken" in get_activity_task_response and \
        get_activity_task_response["taskToken"]


def worker(activity_arn, s3_bucket_name, region_name):
    """Run a worker persistently on a single thread.

    The worker will call get_activity_task repeatedly with delayed retries
    until it gets a response from the cbm3_aws state machine.


        ::task input format (the content of activity_task_response["input"])

            "upload_s3_key": "string",
            "simulations":[
                {"project_code": "string", "simulation_ids": [integer]}
            ]

    Args:
        activity_arn (string): the resource name for the activity task to poll
        s3_bucket_name (string): the name of the s3 bucket to get input data
            from and to upload results to
        region_name (string): AWS region name
    """

    # config here is based on the AWS recommendation found in the boto
    # docs, and the pull request here:
    # https://github.com/boto/botocore/pull/634
    client = boto3.client(
        'stepfunctions', region_name=region_name,
        config=Config(connect_timeout=65, read_timeout=65))

    while True:

        get_activity_task_response = client.get_activity_task(
            activityArn=activity_arn)

        retry_interval = 30
        if not __valid_token(get_activity_task_response):
            time.sleep(retry_interval)
            # If there is a null task token it means there is no task
            # available. Sleep the worker and try again
            while not __valid_token(get_activity_task_response):

                get_activity_task_response = client.get_activity_task(
                    activityArn=activity_arn)
                time.sleep(retry_interval)

        task_token = get_activity_task_response["taskToken"]
        task_input = json.loads(get_activity_task_response["input"])
        process_task(client, task_token, task_input["Input"], s3_bucket_name)


def process_task(client, task_token, task_input, s3_bucket_name):
    try:
        heart_beat_stop_flag = Event()
        heart_beat_thread = HeartBeatThread(
            heart_beat_stop_flag, 25,
            target_func=lambda:
                client.send_task_heartbeat(taskToken=task_token))
        heart_beat_thread.start()

        with tempfile.TemporaryDirectory() as temp_dir:
            s3_working_dir = os.path.join(temp_dir, "s3_working")
            os.makedirs(s3_working_dir)

            s3_io = S3IO(
                execution_s3_key_prefix=task_input["upload_s3_key"],
                s3_interface=S3Interface(
                    s3_resource=boto3.resource('s3'),
                    bucket_name=s3_bucket_name,
                    local_temp_dir=s3_working_dir))

            cbm3_working_dir = os.path.join(temp_dir, "cbm3_working")
            os.makedirs(cbm3_working_dir)

            instance_cbm3_task.run_tasks(
                simulation_tasks=task_input["simulations"],
                local_working_dir=cbm3_working_dir,
                s3_io=s3_io)

        client.send_task_success(
            taskToken=task_token,
            output=json.dumps({"output": task_input["simulations"]}))
    except Exception:
        client.send_task_failure(
            taskToken=task_token,
            error="Exception",
            cause=traceback.format_exc())
        heart_beat_stop_flag.set()
        time.sleep(60)
    finally:
        if not heart_beat_stop_flag.is_set():
            heart_beat_stop_flag.set()
