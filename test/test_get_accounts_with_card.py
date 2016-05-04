# -*- coding: utf-8 -*-
import changer
import unittest
from lxml import etree


class TestGetAccountsWithCard(unittest.TestCase):
    def test_bad_xml(self):
        with self.assertRaises(etree.XMLSyntaxError):
            changer.get_accounts_with_card("<spam>")

    def test_good_xml(self):
        file = open('test/get_account_xml_good.xml', 'r')
        file_xml = file.read()
        result = changer.get_accounts_with_card(file_xml)
        self.assertEqual(result, ["1234"])
        file.close()

if __name__ == '__main__':
    unittest.main()
