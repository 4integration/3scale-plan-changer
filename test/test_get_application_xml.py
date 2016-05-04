# -*- coding: utf-8 -*-
import changer
import unittest
import requests_mock


class TestGetApplicationXml(unittest.TestCase):
    def test_500_response(self):
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, text='Ahh Panic!!!', status_code=500)
            result = changer.get_application_xml('1234', 'fake-key', 'myapp.3scale.net')
            self.assertEqual(result, None)

    def test_418_response(self):
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, text='Herp derp I\'m a teapot', status_code=418)
            result = changer.get_application_xml('1234', 'fake-key', 'myapp.3scale.net')
            self.assertEqual(result, None)

    def test_200_response(self):
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, text='I\'m some XML honest', status_code=200)
            result = changer.get_application_xml('1234', 'fake-key', 'myapp.3scale.net')
            self.assertEqual(result, 'I\'m some XML honest')

if __name__ == '__main__':
    unittest.main()
