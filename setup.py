import os
from setuptools import setup
from setuptools import find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

console_scripts = [
    "cbm3_aws_instance = cbm3_aws.scripts.run_instance:main"
]

setup(
    name="cbm3_aws",
    version="0.1.0",
    description="Scripts for running CBM3 simulations on AWS",
    keywords=["cbm-cfs3", "AWS"],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="",
    download_url="",
    packages=find_packages(exclude=['test*']),
    entry_points={
        "console_scripts": console_scripts
    },
    install_requires=requirements
)
