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

    def test_sidtoid_grous_withid(self):
        # isys
        self.assertEqual(idmap.sidtoid("S-1-5-21-1117850145-1682116191-196506527-26307"),"GID:4640")

    def test_sidtoid_grous_withoutid(self):
        # ISYS_Admin
        self.assertEqual(idmap.sidtoid("S-1-5-21-1117850145-1682116191-196506527-26620"),"GID:10026620")

if __name__ == '__main__':
    unittest.main()
