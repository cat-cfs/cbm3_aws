import os
from setuptools import setup
from setuptools import find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

console_scripts = [
    "cbm3_aws_instance = cbm3_aws.scripts.run_instance:main",
    "cbm3_aws_instance_process = cbm3_aws.scripts.instance_process:main",
    "cbm3_aws_deploy = cbm3_aws.scripts.aws_deploy:main",
    "cbm3_aws_cleanup = cbm3_aws.scripts.aws_cleanup:main",
    "cbm3_aws_start_execution = cbm3_aws.scripts.start_execution:main",
    "cbm3_aws_s3_upload = cbm3_aws.scripts.s3_upload:main"
]

package_data = [
    os.path.join("instance", "instance_prep_software.json"),
    os.path.join("instance", "instance_prep.ps1"),
]
setup(
    name="cbm3_aws",
    version="0.7.0",
    description="Scripts for running CBM3 simulations on AWS",
    keywords=["cbm-cfs3", "AWS"],
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['test*']),
    entry_points={
        "console_scripts": console_scripts
    },
    package_data={"cbm3_aws": package_data},
    install_requires=requirements
)
