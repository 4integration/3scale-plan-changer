# -*- coding: utf-8 -*-
import approver
import unittest


class TestCheckApplicationStatus(unittest.TestCase):
    def test_bad_xml(self, *args):
        result = approver.get_pending_applications("<spam>")
        self.assertEqual(result, None)

    def test_good_xml(self, *args):
        file = open('test/check_application_status_good.xml', 'r')
        file_xml = file.read()
        result = approver.get_pending_applications(file_xml)
        self.assertEqual(result, ["12345"])
        file.close()

if __name__ == '__main__':
    unittest.main()
