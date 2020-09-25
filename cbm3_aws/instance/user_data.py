
def create_userdata(activity_arn, s3_bucket_name):
    """Creates the script to run at the start of each instance worker,
    passed to the ec2 instance launch user-data parameter.

    Returns:
        str: lines of commands to run in AWS EC2 user-data at EC2 startup
    """
    commands = [
        "<script>",
        "pip install git+https://github.com/cat-cfs/cbm3_python",
        "pip install git+https://github.com/cat-cfs/cbm3_aws",
        "cbm3_aws_instance "
        "shutdown /s",
        "</script>"
    ]
    return "\n".join(commands)