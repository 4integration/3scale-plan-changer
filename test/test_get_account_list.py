# -*- coding: utf-8 -*-
import changer
import unittest
import requests_mock
import requests


class TestGetAccountList(unittest.TestCase):
    def test_500_response(self):
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, text='Ahh Panic!!!', status_code=500)
            with self.assertRaises(requests.HTTPError):
                changer.get_account_list('fake-key', 'myapp.3scale.net')

    def test_418_response(self):
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, text='Herp derp I\'m a teapot', status_code=418)
            with self.assertRaises(requests.HTTPError):
                changer.get_account_list('fake-key', 'myapp.3scale.net')

    def test_200_response(self):
        with requests_mock.Mocker() as m:
            file = open('test/get_account_xml_good.xml', 'r')
            file_xml = file.read()
            file.close()
            m.get(requests_mock.ANY, text=file_xml, status_code=200)
            result = changer.get_account_list('fake-key', 'myapp.3scale.net')
            self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()
