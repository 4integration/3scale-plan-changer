# -*- coding: utf-8 -*-
import changer
import unittest
import requests_mock


class TestChangeApplicationPlan(unittest.TestCase):
    def test_500_response(self):
        with requests_mock.Mocker() as m:
            m.put(requests_mock.ANY, status_code=500)
            result = changer.change_application_plan('12345', '1234', '1234', 'fake-key', 'myapp.3scale.net')
            self.assertEqual(result, None)

    def test_200_response(self):
        with requests_mock.Mocker() as m:
            m.put(requests_mock.ANY, status_code=200)
            result = changer.change_application_plan('12345', '1234', '1234', 'fake-key', 'myapp.3scale.net')
            self.assertEqual(result, None)

if __name__ == '__main__':
    unittest.main()
