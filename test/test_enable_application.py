# -*- coding: utf-8 -*-
import approver
import unittest
import requests_mock


class TestEnableApplication500(unittest.TestCase):
    def test_500_response(self):
        with requests_mock.Mocker() as m:
            m.put(requests_mock.ANY, status_code=500)
            result = approver.enable_application('12345', '1234', 'fake-key', 'myapp.3scale.net')
            self.assertEqual(result, None)

    def test_200_response(self):
        with requests_mock.Mocker() as m:
            m.put(requests_mock.ANY, status_code=200)
            result = approver.enable_application('12345', '1234', 'fake-key', 'myapp.3scale.net')
            self.assertEqual(result, None)

if __name__ == '__main__':
    unittest.main()
