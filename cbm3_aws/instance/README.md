# instance set up

In order to run CBM3 the instance needs software installed.  This package `cbm3_aws.instance` has modules for helping with instance preparation.

Use the `cbm3_aws.instance.instance_prep`` module to upload the required software to the cat-cfs bucket, and generate a userdata script at the path: `"user_data_script.txt"`

Create an instance and set the user data field to the user data script text.
After the instance configures and shuts down create an AMI from the instance, and delete the instance.  The AMI's identifier can be passed to the `cbm3_aws.scripts.aws_deploy` command line interface.

**IMPORTANT**

When launching with the above user data the EC2 Instance will require a role with access to the s3 bucket