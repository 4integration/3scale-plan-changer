# -*- coding: utf-8 -*-
import changer
import unittest
from lxml import etree


class TestGetFreePlanApplications(unittest.TestCase):
    def test_bad_xml(self):
        with self.assertRaises(etree.XMLSyntaxError):
            changer.get_free_plan_applications("<spam>", "12345678")

    def test_good_xml(self):
        file = open('test/applications_good.xml', 'r')
        file_xml = file.read()
        result = changer.get_free_plan_applications(file_xml, "12345678")
        self.assertEqual(result, ["12345"])
        file.close()

    def test_good_xml_no_match(self):
        file = open('test/applications_good.xml', 'r')
        file_xml = file.read()
        result = changer.get_free_plan_applications(file_xml, "128401825")
        self.assertEqual(result, None)
        file.close()

if __name__ == '__main__':
    unittest.main()
