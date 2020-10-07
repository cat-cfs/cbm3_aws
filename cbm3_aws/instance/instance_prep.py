import os
import json
import base64
from urllib import request
from io import BytesIO


def download_file(url, local_file_path):
    response = request.urlopen(url)
    with open(local_file_path, 'wb') as local_file:
        local_file.write(BytesIO(response.read()).read())


def upload_to_s3(s3_interface, local_software_dir):
    s3_interface.upload_compressed(
        key_name_prefix="instance_prep",
        document_name="instance_software",
        local_path=local_software_dir)


def load_software_list():
    software_list_path = os.path.join(
        get_local_dir(), "instance_prep_software.json")
    with open(software_list_path) as software_list_file:
        return json.load(software_list_file)["software_list"]


def process_files(s3_interface, local_software_dir):
    for software in load_software_list():
        download_file(
            url=software["url"],
            local_file_path=os.path.join(
                local_software_dir, software["file_name"]))

    upload_to_s3(s3_interface, local_software_dir)


def get_local_dir():
    """Gets the directory containing this script
    Returns:
        str: full path to the the script's directory
    """
    return os.path.dirname(os.path.realpath(__file__))


def get_userdata(bucket_name, base64_encode=False):
    """Returns a string, optionally base64 encoded to be run in the user-data
    field of an EC2 instance in order to prepare the OS for running CBM3 and a
    cbm3_aws worker script

    Args:
        bucket_name (str): name of bucket from which the instance can download
            the required software.
        base64_encode (bool, optional): If set to true the returned string is base64
            encoded. Defaults to False.

    Returns:
        str: the user data script
    """
    ps1_script_path = os.path.join(get_local_dir(), "instance_prep.ps1")
    ps1_variables = [
        f'Set-Variable "s3bucket" -Value "{bucket_name}"'
    ]
    with open(ps1_script_path) as ps1_script_file:
        ps1_script = ps1_script_file.read()

    user_data_script = '\n'.join([
        '<powershell>'
        '\n'.join(ps1_variables),
        ps1_script,
        '</powershell>'
    ])

    if base64_encode:
        return base64.b64encode(user_data_script.encode()).decode("ascii")
    return user_data_script
