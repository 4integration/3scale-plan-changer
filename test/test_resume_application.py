# -*- coding: utf-8 -*-
import changer
import unittest
import requests_mock
import requests


class TestResumeApplication(unittest.TestCase):
    def test_500_response(self):
        with requests_mock.Mocker() as m:
            m.put(requests_mock.ANY, status_code=500)
            with self.assertRaises(requests.HTTPError):
                changer.resume_application('12345', '1234', 'fake-key', 'myapp.3scale.net')

    def test_200_response(self):
        with requests_mock.Mocker() as m:
            m.put(requests_mock.ANY, status_code=200)
            result = changer.resume_application('12345', '1234', 'fake-key', 'myapp.3scale.net')
            self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()
