# cbm3_aws

Scripts and commands for deploying and running CBM3 simulations on AWS

## Instance Requirements

* The [CBM-CFS3 toolbox](https://www.nrcan.gc.ca/climate-change/impacts-adaptations/climate-change-impacts-forests/carbon-accounting/carbon-budget-model/13107)
* The Windows operating system
* python 3x
* python packages (see requirements.txt)

## Installing

The scripts can be directly installed from github

```bash
pip install git+https://github.com/cat-cfs/cbm3_aws.git
```

## Deploying the cluster

Deploy a cbm3_aws cluster from the windows command line

```
cbm3_aws_deploy ^
    --region_name ca-central-1 ^
    --s3_bucket_name my-cbm3-aws-bucket ^
    --min_instances 1 ^
    --max_instances 1 ^
    --image_ami_id ami-0c2f25c1f66a1ff4d ^
    --instance_type t2.micro ^
    --resource_description_path .\cbm3_aws_resources.json
```

After running this command successfully, a `cbm3_aws` cluster will have been deployed and will await tasks to run.

## Resource Description File

A *resource description file* will be created by the `cbm3_aws_deploy` command at the path specified in the command. This file contains identifying information for all resources allocated.

Example resources file

```json
{
    "uuid": "<uuid>",
    "names": {
        "run_activity": "cbm3_run_activity_<uuid>",
        "autoscale_launch_template": "cbm3_run_launch_template_<uuid>",
        "autoscale_group": "cbm3_autoscale_group_<uuid>",
        "run_task_state_machine": "cbm3_run_task_state_machine_<uuid>",
        "run_state_machine": "cbm3_run_state_machine_<uuid>"
    },
    "region_name": "ca-central-1",
    "s3_bucket_name": "my-cbm3-aws-bucket",
    "min_virtual_cpu": 1,
    "max_virtual_cpu": 1,
    "image_ami_id": "ami-0c2f25c1f66a1ff4d",
    "instance_type": "t2.micro",
    "s3_bucket_policy_context": {
        "policy_arn": "arn:aws:iam::<account#>:policy/cbm3_s3_instance_policy"
    },
    "state_machine_policy_context": {
        "policy_arn": "arn:aws:iam::<account#>:policy/cbm3_state_machine_policy"
    },
    "instance_iam_role_context": {
        "role_arn": "arn:aws:iam::<account#>:role/cbm3_instance_iam_role",
        "role_name": "cbm3_instance_iam_role"
    },
    "state_machine_role_context": {
        "role_arn": "arn:aws:iam::<account#>:role/cbm3_state_machine_role",
        "role_name": "cbm3_state_machine_role"
    },
    "state_machine_context": {
        "activity_arn": "arn:aws:states:ca-central-1:<account#>:activity:cbm3_run_activity_<uuid>",
        "task_state_machine_arn": "arn:aws:states:ca-central-1:<account#>:stateMachine:cbm3_run_task_state_machine_<uuid>",
        "app_state_machine_arn": "arn:aws:states:ca-central-1:<account#>:stateMachine:cbm3_run_state_machine_<uuid>"
    },
    "user_data": "<script><app_run_command></script>"
}
```



## Clean up the cluster

Whether or not the cbm3_aws_deploy command executed successfully or not, the cluster, or partially allocated cluster, can be deallocated with the following command passing the `resource description file` created by the `cbm3_aws_deploy` command.

```
cbm3_aws_cleanup --resource_description_path .\cbm3_aws_resources.json
```

If the above command runs successfully the resource file is no longer needed:

```
del .\cbm3_aws_resources.json
```

**Note: This does not remove the s3 bucket named in the  `cbm3_aws_deploy` and this must be done as a separate step.**

## Start an execution on a running cluster
