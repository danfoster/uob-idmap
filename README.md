# Custom Samba IDMAP Script for UoB

The script `idmap.py` provides a suitable `SID<->UID/GID` for Users and Groups in Active Directory at the University of Bristol. It is compatible with the [`idmap_tdb2`](https://www.samba.org/samba/docs/man/manpages/idmap_tdb2.8.html) backend. 

## Usage

### Authentication

A service user is required to bind to the AD LDAP interface. This should be defined in either `/etc/idmap.yaml` or `~/.idmap.yaml` and takes the following format:

```
---
adusername: serviceuser@ad.example.com
adpassword: ******
adserver: ldap://ad.example.com
```

### Samba config

Configure `smb.conf` to use the `tdb2` backend for your domain and call the `idmap.py` script. For example:

```
security = ads
passdb backend = tdbsam
winbind expand groups = 1
template shell=/bin/bash
template homedir=/home/%U
winbind use default domain=true
winbind offline logon=false
winbind refresh tickets=yes
winbind enum users=no
winbind enum groups=no
winbind nested groups=yes
idmap negative cache time=60
winbind max domain connections=16
idmap config UOB:backend=tdb2
idmap config UOB:range=336-4294967295
idmap config UOB:script = /usr/local/bin/idmap.py
idmap config *:backend=tdb
idmap config *:range=4294967296-4394967294
```


## Requirements

CentOS package names:
 
 * `PyYAML`
 * `python-ldap`

## Background

The University of Bristol, like many organisations has an upstream IdM system above Active Directory. Real users and structured groups are created here and propagated to a number of different presentation layers, including Active Directory. Users and groups provisioned in this way have appropriate UIDs and GIDs assigned to them for use on unix systems.

In addition, adhoc groups and some users are created directly in AD. These objects do not have a UID or GID assigned to them.

It had been decided that when a unix system is consuming users and groups from AD the following rules:
 1. If `uidNumber` for `users` or `gidNumber` for `groups` is defined, this must be used
 2. Otherwise, take the `RID` and add `10,000,000`.

These 2 stages each fit nicely with existing samba `idmap` modules, namely `idmap_ad` and `idmap_rid`. Unfortunately it is not possible to chain multiple `idmap` backends together. Therefore this script, for use with `idmap_tdb2` was created to provide this functionality.
