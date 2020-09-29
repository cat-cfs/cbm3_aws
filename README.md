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
    --s3_bucket_name my_cbm3_aws_bucket ^
    --min_instances 1 ^
    --max_instances 1 ^
    --image_ami_id ami-00000 ^
    --instance_type i3.large ^
    --resource_description_path .\cbm3_aws_resources.json
```

After running this command successfully, a `cbm3_aws` cluster will have been deployed and will await tasks to run. 

A *resource description file* will be created by the `cbm3_aws_deploy` command at the path specified in the command. This file contains identifying information for all resources allocated.

Example resources file

```json
{
    "uuid": "fqcgE8SBvU4WEW9NGVhVek",
    "names": {
        "run_activity": "cbm3_run_activity_fqcgE8SBvU4WEW9NGVhVek",
        "autoscale_launch_template": "cbm3_run_launch_template_fqcgE8SBvU4WEW9NGVhVek",
        "autoscale_group": "cbm3_autoscale_group_fqcgE8SBvU4WEW9NGVhVek",
        "run_task_state_machine": "cbm3_run_task_state_machine_fqcgE8SBvU4WEW9NGVhVek",
        "run_state_machine": "cbm3_run_state_machine_fqcgE8SBvU4WEW9NGVhVek"
    },
    "region_name": "ca-central-1",
    "s3_bucket_name": "my_cbm3_aws_bucket",
    "min_instances": "1",
    "max_instances": "1",
    "image_ami_id": "ami-00000",
    "instance_type": "i3.large"
}
```



## Clean up the cluster

Whether or not the cbm3_aws_deploy command executed successfully or not, the cluster, or partially allocated cluster, can be deallocated with the following command passing the `resource description file` created by the `cbm3_aws_deploy` command.

```
cbm3_aws_cleanup --resource_description_path .\cbm3_aws_resources.json
```





