# -*- coding: utf-8 -*-
import changer
import unittest
from lxml import etree
from datetime import datetime


class TestGetAccountsWithoutCard(unittest.TestCase):
    def test_bad_xml(self):
        with self.assertRaises(etree.XMLSyntaxError):
            changer.get_accounts("<spam>")

    def test_good_xml(self):
        file = open('test/get_account_xml_good.xml', 'r')
        file_xml = file.read()
        result = changer.get_accounts(file_xml, card=False)
        self.assertEqual(result,
                         [tuple(("1235", datetime.strptime('2015-02-28T19:50:04+0000', '%Y-%m-%dT%H:%M:%S%z')))])
        file.close()


if __name__ == '__main__':
    unittest.main()
