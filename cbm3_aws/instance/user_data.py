
def create_userdata(activity_arn, s3_bucket_name):
    """Creates the script to run at the start of each instance worker,
    passed to the ec2 instance launch user-data parameter.

    Returns:
        str: lines of commands to run in AWS EC2 user-data at EC2 startup
    """

    instance_run_script_command = \
        "cbm3_aws_instance " \
        f"--activity_arn {activity_arn} " \
        f"--s3_bucket_name {s3_bucket_name}"

    commands = [
        "<script>",
        "pip install git+https://github.com/cat-cfs/cbm3_python",
        "pip install git+https://github.com/cat-cfs/cbm3_aws",
        instance_run_script_command,
        "shutdown /s",
        "</script>"
    ]
    return "\n".join(commands)