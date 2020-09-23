import os
import time
import tempfile
import sys
from multiprocessing import Process
import boto3
from botocore.client import Config
from cbm3_aws.instance import instance_cbm3_task
from cbm3_aws.s3_interface import S3Interface


def heartbeat(task_token):
    client = boto3.client('stepfunctions')
    start_time = time.time()
    while True:
        client.send_task_heartbeat(
            taskToken=task_token)
        time.sleep(60.0 - ((time.time() - start_time) % 60.0))


def run(activity_arn, s3_bucket_name):

    # config here is based on the AWS recommendation found in the boto docs,
    # and the pull request here:
    # https://github.com/boto/botocore/pull/634
    client = boto3.client(
        'stepfunctions', config=Config(connect_timeout=65, read_timeout=65))

    get_activity_task_response = client.get_activity_task(
        activityArn=activity_arn)

    task_token = get_activity_task_response["taskToken"]
    heart_beat_process = Process(
        target=heartbeat, args=(task_token,))
    heart_beat_process.start()

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            s3_working_dir = os.path.join(temp_dir, "s3_working")
            os.makedirs(s3_working_dir)

            s3_interface = S3Interface(
                s3_resource=boto3.resource('s3'),
                bucket_name=s3_bucket_name,
                local_temp_dir=s3_working_dir)

            cbm3_working_dir = os.path.join(temp_dir, "cbm3_working")
            os.makedirs(cbm3_working_dir)
            task_input = get_activity_task_response["input"]
            instance_cbm3_task.run_tasks(
                task_message=task_input,
                local_working_dir=cbm3_working_dir,
                s3_interface=s3_interface)
            client.send_task_success(
                taskToken=task_token,
                output=task_input)
    except Exception:
        if task_token:
            client.send_task_failure(
                taskToken=task_token,
                error="error",
                cause=sys.exc_info()[0])

    finally:
        heart_beat_process.kill()