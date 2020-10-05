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



Since it's unclear that this has a permanent download link, it is included in the instance resources dir



https://www.microsoft.com/en-ca/download/confirmation.aspx?id=13255&6B49FDFB-8E5B-4B07-BC31-15695C5A2143=1



## Sysprep

https://aws.amazon.com/premiumsupport/knowledge-center/sysprep-create-install-ec2-windows-amis/