# -*- coding: utf-8 -*-
import approver
import unittest


class TestGetAccountsWithCard(unittest.TestCase):
    def test_bad_xml(self, *args):
        result = approver.get_accounts_with_card("<spam>")
        self.assertEqual(result, None)

    def test_good_xml(self, *args):
        file = open('test/get_account_xml_good.xml', 'r')
        file_xml = file.read()
        result = approver.get_accounts_with_card(file_xml)
        self.assertEqual(result, ["1234"])
        file.close()

if __name__ == '__main__':
    unittest.main()
