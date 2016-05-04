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
    """Downloads the list of approved customer accounts from 3Scale for our provider key and api endpoint and returns
    the XML as a string. May return None if we get an error code from 3Scale.

    :param str provider_key: The 3Scale Provider Key
    :param str api_endpoint: The 3Scale API Endpoint

    :return: Customer accounts XML response
    :rtype str or None
    """

    r = requests.get('https://' + api_endpoint + '/admin/api/accounts.xml?provider_key=' + provider_key +
                     '&state=approved')
    if r.status_code != 200:
        print("Error: Code " + str(r.status_code) + " while getting account xml from 3scale")
        return None

    return r.text


def get_accounts_with_card(account_xml):
    """Processes the 3Scale list of customer accounts and returns the id for any that have credit cards stored.

    :param str account_xml: The 3Scale Response XML with a list of customer accounts.

    :return: List of 3Scale account ids.
    :rtype: list[str]
    """
    try:
        root = etree.fromstring(account_xml.encode('utf-8'))
    except etree.XMLSyntaxError:
        print("Error: XML Syntax Error in 3Scale accounts response")
        return None

    account_objects = root.findall("account")
    account_list = []

    for account_object in account_objects:
        credit_card_status = account_object.find("credit_card_stored")
        if credit_card_status.text == "true":
            account_id = account_object.find("id")
            account_list.append(account_id.text)

    return account_list


def get_application_xml(account_id, provider_key, api_endpoint):
    """Downloads the list of applications from 3Scale for a given account_id and returns the XML as a string. May return
     None if we get an error code from 3Scale.

    :param str account_id: The 3Scale Customer Account ID.
    :param str provider_key: The 3Scale Provider Key
    :param str api_endpoint: The 3Scale API Endpoint

    :return: Applications XML response
    :rtype str or None
    """

    r = requests.get('https://' + api_endpoint + '/admin/api/accounts/' + account_id +
                     '/applications.xml?provider_key=' + provider_key)

    if r.status_code != 200:
        print("Error: Code " + str(r.status_code) + " while getting application xml for account " + account_id)
        return None

    return r.text


def check_application_status(application_xml):
    """Processes the applications xml and returns the id for any that are pending.

    :param str application_xml: The 3Scale Response XML with a list of applications for a account.

    :return: List of applications that are Pending
    :rtype: list[str] or None
    """

    try:
        root = etree.fromstring(application_xml.encode('utf-8'))
    except etree.XMLSyntaxError:
        print("Error: XML Syntax Error in 3Scale applications response")
        return None

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
    """Sends a request to 3scale to accept an application.

    :param str account_id: The 3Scale Customer Account ID.
    :param str application_id: The 3Scale Application ID.
    :param str provider_key: The 3Scale Provider Key
    :param str api_endpoint: The 3Scale API Endpoint

    :return: None
    :rtype: NoneType
    """

    print("Accepting application " + application_id + " for account " + account_id)
    r = requests.put('https://' + api_endpoint + '/admin/api/accounts/' + account_id + '/applications/' +
                     application_id + '/accept.xml', data={'provider_key': provider_key})

    if r.status_code == 200:
        print("Success accepting application for " + application_id + " for account " + account_id)
    else:
        print("Error: Code " + str(r.status_code) + " while accepting application for " + application_id +
              " for account " + account_id)


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
    if not isinstance(accounts, list):
        print("Warning: No accounts found with card details stored")
        exit(0)
    else:
        for account in accounts:
            applications = check_application_status(get_application_xml(account, threescale_provider_key,
                                                                        threescale_api_endpoint))
            if applications:
                for application in applications:
                    enable_application(account, application, threescale_provider_key, threescale_api_endpoint)
