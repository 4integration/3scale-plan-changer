# -*- coding: utf-8 -*-
"""
    3Scale Application Approver
    ~~~~~~~~~~~~~~
    Approves pending applications for 3scale accounts that have credit card information.

    :copyright: (c) 2016 Snowflake Software Limited.
    :license: MIT, see LICENSE for more details.
"""

import requests
from lxml import etree
import argparse


def get_account_xml(provider_key, api_endpoint):
    r = requests.get('https://' + api_endpoint + '/admin/api/accounts.xml?provider_key=' + provider_key +
                     '&state=approved')
    if r.status_code != 200:
        print("Error " + r.status_code + " getting account xml from 3scale")
        return None

    return r.text


def get_accounts_with_card(account_xml):
    root = etree.fromstring(account_xml.encode('utf-8'))
    account_objects = root.findall("account")
    account_list = []

    for account_object in account_objects:
        credit_card_status = account_object.find("credit_card_stored")
        if credit_card_status.text == "true":
            account_id = account_object.find("id")
            account_list.append(account_id.text)

    return account_list


def get_application_xml(account_id, provider_key, api_endpoint):
    r = requests.get('https://' + api_endpoint + '/admin/api/accounts/' + account_id +
                     '/applications.xml?provider_key=' + provider_key)

    if r.status_code != 200:
        print("Error" + r.status_code + " getting application xml for account " + account_id)
        return None

    return r.text


def check_application_status(application_xml):
    root = etree.fromstring(application_xml.encode('utf-8'))
    application_objects = root.findall("application")
    application_list = []
    for application_object in application_objects:
        state = application_object.find("state").text
        if state == "pending":
            application_id = application_object.find("id").text
            application_list.append(application_id)
            print("Found pending application " + application_id)

    if not application_list:
        return None
    else:
        return application_list


def enable_application(account_id, application_id, provider_key, api_endpoint):
    print("Accepting application " + application_id + " for account " + account_id)
    r = requests.put('https://' + api_endpoint + '/admin/api/accounts/' + account_id + '/applications/' +
                     application_id + '/accept.xml', data={'provider_key': provider_key})

    if r.status_code == 200:
        print("Accepting application worked for " + application_id + " for account " + account_id)
    else:
        print("Error " + r.status_code + " accepting application for " + application_id + " for account " + account_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider_key', help='A 3Scale Provider Key')
    parser.add_argument('--api_endpoint', help='A 3Scale API Endpoint e.g. myapp.3scale.net')

    args = parser.parse_args()

    threescale_provider_key = args.provider_key
    threescale_api_endpoint = args.api_endpoint

    if not threescale_api_endpoint or not threescale_api_endpoint:
        print("Error: Missing argument. Please see --help.")
        exit(1)

    accounts = get_accounts_with_card(get_account_xml(threescale_provider_key, threescale_api_endpoint))
    for account in accounts:
        applications = check_application_status(get_application_xml(account, threescale_provider_key,
                                                                    threescale_api_endpoint))
        if applications:
            for application in applications:
                enable_application(account, application, threescale_provider_key, threescale_api_endpoint)
