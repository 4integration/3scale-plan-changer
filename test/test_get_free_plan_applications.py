# -*- coding: utf-8 -*-
import changer
import unittest


class TestGetFreePlanApplications(unittest.TestCase):
    def test_bad_xml(self):
        result = changer.get_free_plan_applications("<spam>", "12345678")
        self.assertEqual(result, None)

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
