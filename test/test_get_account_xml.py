# -*- coding: utf-8 -*-
import approver
import unittest
import requests_mock


class TestGetAccountXml500(unittest.TestCase):
    def test_500_response(self):
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, text='Ahh Panic!!!', status_code=500)
            result = approver.get_account_xml('fake-key', 'myapp.3scale.net')
            self.assertEqual(result, None)

    def test_418_response(self):
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, text='Herp derp I\'m a teapot', status_code=418)
            result = approver.get_account_xml('fake-key', 'myapp.3scale.net')
            self.assertEqual(result, None)

if __name__ == '__main__':
    unittest.main()
