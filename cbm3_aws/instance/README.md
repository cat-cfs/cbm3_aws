# instance set up

In order to run CBM3 the instance needs software installed.  This package `cbm3_aws.instance` has modules for helping with instance preparation.


## python 3x

https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe


## Enable .net 2.0/3.5

The CBM-CFS3 toolbox needs this older version of .NET enabled to run.

These commands enable this on windows server 2019, 2016, 2012 [source](http://backupchain.com/i/how-to-install-net-framework-2-0-on-windows-server-platforms)

```
DISM /Online /Enable-Feature:NetFx3 /All

Dism /online /enable-feature:NetFX3 /All /Source:X:\sources\sxs
```


## MS Access driver


https://download.microsoft.com/download/2/4/3/24375141-E08D-4803-AB0E-10F2E3A07AAA/AccessDatabaseEngine_X64.exe


## Current method

run this script

```python
import boto3
import os
from cbm3_aws.s3_interface import S3Interface
from cbm3_aws.instance import instance_prep

s3_bucket_name="cat-cfs"
local_temp_dir=os.path.abspath(r".\s3_temp")
local_software_dir=os.path.abspath(r".\local_software")

s3_interface = S3Interface(
    s3_resource=boto3.resource('s3'),
    bucket_name=s3_bucket_name,
    local_temp_dir=local_temp_dir)

instance_prep.upload_software(
    s3_interface=s3_interface,
    local_software_dir=local_software_dir)

with open("user_data_script.txt", 'w') as user_data_script_fp:
    user_data_script_fp.write(
        instance_prep.get_userdata(s3_bucket_name))
```

This will upload the required software to the cat-cfs bucket, and generate a userdata script at the path: `"user_data_script.txt"`

Create an instance and set the user data field to the user data script text.
After the instance configures and shuts down create an AMI from the instance, and delete the instance.  The AMI's identifier can be passed to the `cbm3_aws.scripts.aws_deploy` command line interface.
