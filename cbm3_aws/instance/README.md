# instance set up

The following commands must be run to prepare an instance for running CBM3

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



## Sysprep

https://aws.amazon.com/premiumsupport/knowledge-center/sysprep-create-install-ec2-windows-amis/