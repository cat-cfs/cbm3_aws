import base64


def create_userdata(
    activity_arn: str, s3_bucket_name: str, region_name: str
) -> str:
    """Creates the script to run at the start of each instance worker,
    passed to the ec2 instance launch user-data parameter.

    Returns:
        str: lines of commands to run in AWS EC2 user-data at EC2 startup
    """

    instance_run_script_command = (
        "cbm3_aws_instance "
        f"--activity_arn {activity_arn} "
        f"--s3_bucket_name {s3_bucket_name} "
        f"--region_name {region_name}"
    )

    commands = [
        "<powershell>",
        "pip install git+https://github.com/cat-cfs/cbm3_python",
        "pip install git+https://github.com/cat-cfs/cbm3_aws",
        instance_run_script_command,
        "</powershell>",
    ]
    userdata = "\n".join(commands)
    return base64.b64encode(userdata.encode()).decode("ascii")
