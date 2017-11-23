# -*- coding: utf-8 -*-
import changer
import unittest
from lxml import etree
from datetime import datetime


class TestGetAccountsWithCard(unittest.TestCase):
    def test_good_xml(self):
        file = open('test/get_account_xml_good.xml', 'r')
        file_xml = file.read()
        file.close()
        root = etree.fromstring(file_xml.encode('utf-8'))
        account_objects = root.findall("account")
        result = changer.get_accounts(account_objects)
        self.assertEqual(result, [tuple(("1234",
                                         datetime.strptime('2015-02-23T19:50:04+0000', '%Y-%m-%dT%H:%M:%S%z')))])


if __name__ == '__main__':
    unittest.main()
