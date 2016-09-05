#!/usr/bin/env python


import ldap
import sys
import argparse
import struct
import base64
import os
import yaml

class Settings:
    def __init__(self):
        settingspaths = ["~/.idmap.yaml","/etc/idmap.yaml"]
        finalpath = None
        for path in settingspaths:
            if os.path.isfile(os.path.expanduser(path)):
                finalpath = os.path.expanduser(path)
                break
      
        if finalpath == None:
            logger.error("Cannot find config file in any of the following locations:")
            for path in settingspaths:
                logger.error(" - "+path)
            sys.exit(1) 

        settings = yaml.load(open(finalpath))

        # Validate any required settings here.
        if 'adusername' in settings:
            self.adusername = settings['adusername']
        else:
            print "ERROR: adusername not defined"
            sys.exit(1)

        if 'adpassword' in settings:
            self.adpassword = settings['adpassword']
        else:
            print "ERROR: adpassword not defined"
            sys.exit(1)
            
        if 'adserver' in settings:
            self.adserver= settings['adserver']
        else:
            print "ERROR: adserver not defined"
            sys.exit(1)

# https://blogs.msdn.microsoft.com/oldnewthing/20040315-00/?p=40253

def SIDBinToString(binary):
    version = struct.unpack('B', binary[0])[0]
    # I do not know how to treat version != 1 (it does not exist yet)
    assert version == 1, version
    length = struct.unpack('B', binary[1])[0]
    authority = struct.unpack('>Q', '\x00\x00' + binary[2:8])[0]
    string = 'S-%d-%d' % (version, authority)
    binary = binary[8:]
    assert len(binary) == 4 * length
    for i in xrange(length):
        value = struct.unpack('<L', binary[4*i:4*(i+1)])[0]
        string += '-%d' % (value)
    return string

def SIDStringToBin(string):
    parts = string.split('-')
    binary = struct.pack('BB', int(parts[1]), len(parts)-3)
    binary += struct.pack('>Q', int(parts[2]))[2:8]
    for i in xrange(3,len(parts)):
        binary += struct.pack('<L',int(parts[i]))
    return binary

def connectad():
    settings = Settings()
    # Connect to AD via LDAP
    try:
        l = ldap.initialize(settings.adserver)
        l.protocol_version = ldap.VERSION3
        l.set_option(ldap.OPT_REFERRALS,0)
        l.simple_bind_s(settings.adusername, settings.adpassword)
        return l
    except ldap.LDAPError, e:
        print e
        sys.exit(1)

def ridtoid(rid):
    return rid+10000000

def sidtoid(sid):
    try:
        l = connectad()
        attributes = ["uidNumber", "gidNumber", "objectClass", "objectSid"]
        search_filter = "(objectSid=%s)" % sid
        result = l.search_s("dc=ads,dc=bris,dc=ac,dc=uk", ldap.SCOPE_SUBTREE,
                            search_filter, attributes)[0][1]
        if "user" in result["objectClass"]:
            if "uidNumber" in result:
                uid = result["uidNumber"][0]
            else:
                uid = ridtoid(int(sid.split("-")[-1]))
            return "UID:%s" % uid
        elif "group" in result["objectClass"]:
            if "gidNumber" in result:
                gid = result["gidNumber"][0]
            else:
                gid = ridtoid(int(sid.split("-")[-1]))
            return "GID:%s" % gid
    except ldap.LDAPError, e:
        print e
        sys.exit(1)

def idtosid(objecttype,objectid):
    try:
        l = connectad()
        attributes = ["objectSid"]
        if objecttype == "UID":
            search_filter = "(&(uidNumber=%s)(objectClass=user))" % objectid
        else:
            search_filter = "(&(gidNumber=%s)(objectClass=group))" % objectid
        result = l.search_s("dc=ads,dc=bris,dc=ac,dc=uk", ldap.SCOPE_SUBTREE,
                            search_filter, attributes)[0]
        if result[0] != None:
            sid = SIDBinToString(result[1]["objectSid"][0])
            return "SID:%s" % sid
        else:
            r = l.search_s("dc=ads,dc=bris,dc=ac,dc=uk", ldap.SCOPE_SUBTREE,
                            "(objectClass=domain)", ["objectSid"])[0][1]
            sid=SIDBinToString(r["objectSid"][0])
            sid += "-" + str(objectid-10000000)
            return "SID:%s" % sid

    except ldap.LDAPError, e:
        print e
        sys.exit(1)



def idmap():
    parser = argparse.ArgumentParser(description='Samba TDB2 IDMAP script')
    subparsers = parser.add_subparsers(dest="action")
    sidtoid_parser = subparsers.add_parser('SIDTOID')
    sidtoid_parser.add_argument('sid', help='SID')
    idtosid_parser = subparsers.add_parser('IDTOSID')
    idtosid_parser.add_argument('type', help="UID or GID")
    idtosid_parser.add_argument('id', help="ID", type=int)
    args = parser.parse_args()


    if args.action == "SIDTOID":
        print sidtoid(args.sid)
    elif args.action == "IDTOSID":
        print idtosid(args.type,args.id)

if __name__ == '__main__':
    idmap()



