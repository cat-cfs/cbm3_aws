# download zipped software from s3
Read-S3Object -BucketName cat-cfs -Key instance_prep/software.zip ~\software.zip
# unzip archive
Expand-Archive-LiteralPath ~\software.zip -DestinationPath ~\software

#enable .net2.0/3.5
DISM /Online /Enable-Feature:NetFx3 /All
#install python to c:\python38
Start-Process -FilePath ~\software\python-3.8.6-amd64.exe -ArgumentList "/quiet TargetDir=c:\python38 InstallAllUsers=1 PrependPath=1 Include_test=0" -NoNewWindow -Wait
#set python paths for the process
[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\python38")
[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\python38\scripts")

#install access database engine
Start-Process -FilePath ~\software\AccessDatabaseEngine_X64.exe -ArgumentList "/quiet" -NoNewWindow -Wait

# prepare the instance to user user-data on next boot (this is not currently needed since at this point)
C:\ProgramData\Amazon\EC2-Windows\Launch\Scripts\InitializeInstance.ps1 –Schedule

pip install ~\software\numpy-1.19.2+mkl-cp38-cp38-win_amd64.whl

pip install ~\software\cbm3_python-0.6.7-py3-none-any.whl

pip install ~\software\cbm3_aws.whl
