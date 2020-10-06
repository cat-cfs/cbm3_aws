import os
from urllib import request
from io import BytesIO


SOFTWARE_LIST = [
    {
        "name": "python",
        "url": "https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe",
        "file_name": "python-3.9.0-amd64.exe",
        "install_command": [
            "python-3.9.0-amd64.exe", "/quiet", "InstallAllUsers=1",
            "PrependPath=1", "Include_test=0"]
    },
    {
        "name": "MS Access driver",
        "url": "https://download.microsoft.com/download/2/4/3/24375141-E08D-4803-AB0E-10F2E3A07AAA/AccessDatabaseEngine_X64.exe",
        "file_name": "AccessDatabaseEngine_X64.exe",
        "install_command": ["AccessDatabaseEngine_X64.exe", "/quiet"]
    }

]

instance_commands = [
    "Read-S3Object -BucketName cat-cfs -Key instance_prep/software.zip ~\software.zip",
    "Expand-Archive -LiteralPath ~\software.zip -DestinationPath ~\software",
    'Start-Process -FilePath ~\software\python-3.9.0-amd64.exe -ArgumentList "/quiet TargetDir=c:\python InstallAllUsers=1 PrependPath=1 Include_test=0" -NoNewWindow -Wait',
    'Start-Process -FilePath C:\users\Administrator\software\AccessDatabaseEngine_X64.exe -ArgumentList "/quiet" -NoNewWindow -Wait',
    '[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\python")',
    '[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\python\scripts")'
    'pip install C:\Users\Administrator\Downloads\numpy-1.19.2+mkl-cp38-cp38-win_amd64.whl'
    'pip install C:\Users\Administrator\Desktop\cbm3_python-0.6.7-py3-none-any.whl'
    'pip install ?cbm3_aws.whl'
]

def download_file(url, local_file_path):
    response = request.urlopen(url)
    with open(local_file_path, 'wb') as local_file:
        local_file.write(BytesIO(response.read()).read())


def upload_to_s3(s3_interface, local_software_dir):
    s3_interface.upload_compressed(
        key_name_prefix="instance_prep",
        document_name="software",
        local_path=local_software_dir)


def process_files(s3_interface, local_software_dir, software_list):
    for software in software_list:
        download_file(
            url=software["url"],
            local_file_path=os.path.join(
                local_software_dir, software["file_name"]))

    upload_to_s3(s3_interface, local_software_dir)
