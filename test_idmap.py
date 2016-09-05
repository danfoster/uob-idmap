#!/usr/bin/env python

import idmap
import unittest

class TestIDMap(unittest.TestCase):
    def setUp(self):
        pass

    def test_sidtoid_user_withid(self):
        # cn=df3804
        self.assertEqual(idmap.sidtoid("S-1-5-21-1117850145-1682116191-196506527-68110"),"UID:7236")

    def test_sidtoid_user_withoutid(self):
        # cn=df3804-a
        self.assertEqual(idmap.sidtoid("S-1-5-21-1117850145-1682116191-196506527-193431"),"UID:10193431")

    def test_sidtoid_groups_withid(self):
        # isys
        self.assertEqual(idmap.sidtoid("S-1-5-21-1117850145-1682116191-196506527-26307"),"GID:4640")

    def test_sidtoid_groups_withoutid(self):
        # ISYS_Admin
        self.assertEqual(idmap.sidtoid("S-1-5-21-1117850145-1682116191-196506527-26620"),"GID:10026620")

    def test_idtosid_user_withid(self):
        # cn=df3804
        self.assertEqual(idmap.idtosid("UID",7236),"SID:S-1-5-21-1117850145-1682116191-196506527-68110")

    def test_idtosid_user_withoutid(self):
        # cn=df3804-a
        self.assertEqual(idmap.idtosid("UID",10193431),"SID:S-1-5-21-1117850145-1682116191-196506527-193431")

    def test_idtosid_groups_withid(self):
        # isys
        self.assertEqual(idmap.idtosid("GID",4640),"SID:S-1-5-21-1117850145-1682116191-196506527-26307")

    def test_idtosid_groups_withoutid(self):
        # ISYS_Admin
        self.assertEqual(idmap.idtosid("GID",10026620),"SID:S-1-5-21-1117850145-1682116191-196506527-26620")

if __name__ == '__main__':
    unittest.main()
