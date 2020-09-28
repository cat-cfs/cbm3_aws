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
pip install git+https://github.com/smorken/cbm3_aws.git
```

Deploy a cbm3_aws cluster from the windows command line

```
cbm3_aws_deploy ^
    --region_name ca-central-1 ^
    --s3_bucket_name my_cbm3_aws_bucket ^
    --min_instances 1 ^
    --max_instances 1 ^
    --image_ami_id ami-00000 ^
    --instance_type i3.large
```

