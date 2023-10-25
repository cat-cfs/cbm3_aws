## download zipped software from s3
Read-S3Object -BucketName  $s3bucket -Key cbm3_aws/instance_prep/instance_software.zip ~\instance_software.zip
# unzip archive
Expand-Archive -LiteralPath ~\instance_software.zip -DestinationPath ~\software

#enable .net2.0/3.5
DISM /Online /Enable-Feature:NetFx3 /All

#install python 
Start-Process -FilePath ~\software\python-3.11.6-amd64.exe -ArgumentList "/quiet TargetDir=c:\python311 InstallAllUsers=1 PrependPath=1 Include_test=0" -NoNewWindow -Wait
#set python paths for the process
[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\python311")
[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\python311\scripts")
#helps with installing other package wheels
pip install wheel

Start-Process -FilePath ~\software\Git-2.42.0.2-64-bit.exe -ArgumentList "/SILENT /DIR='c:\git'" -NoNewWindow -Wait
[Environment]::SetEnvironmentVariable("Path", "$env:Path;c:\git\cmd")

#install access database engine
Start-Process -FilePath ~\software\AccessDatabaseEngine_X64.exe -ArgumentList "/quiet" -NoNewWindow -Wait

## prepare the instance to user user-data on next boot
C:\ProgramData\Amazon\EC2-Windows\Launch\Scripts\InitializeInstance.ps1 -Schedule

# shut down the instance after the above steps have completed, so that an AMI can be prepared base on the instance
shutdown /s
