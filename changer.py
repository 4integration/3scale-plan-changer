# -*- coding: utf-8 -*-
"""
    3Scale Plan Changer
    ~~~~~~~~~~~~~~~~~~~
    A simple app that uses the 3Scale API to change application plans when the associated account has credit card
    information stored.

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
    try:
        r = requests.get('https://' + api_endpoint + '/admin/api/accounts.xml?provider_key=' + provider_key +
                         '&state=approved', timeout=5)
    except requests.RequestException:
        print("Error: Exception raised while getting account xml from 3scale")
        raise

    if r.status_code != 200:
        print("Error: Code " + str(r.status_code) + " while getting account xml from 3scale")
        raise requests.HTTPError

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
        raise

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
    try:
        r = requests.get('https://' + api_endpoint + '/admin/api/accounts/' + account_id +
                         '/applications.xml?provider_key=' + provider_key, timeout=5)
    except requests.RequestException:
        print("Error: Exception raised while getting application xml for account " + account_id)
        raise

    if r.status_code != 200:
        print("Error: Code " + str(r.status_code) + " while getting application xml for account " + account_id)
        raise requests.HTTPError

    return r.text


def get_free_plan_applications(application_xml, free_plan):
    """Processes the applications xml and returns the id for any that are in our free plan.

    :param str application_xml: The 3Scale Response XML with a list of applications for an account.
    :param str free_plan: The 3Scale plan that we're changing from.

    :return: List of applications that are in our free plan
    :rtype: list[str] or None
    """

    try:
        root = etree.fromstring(application_xml.encode('utf-8'))
    except etree.XMLSyntaxError:
        print("Error: XML Syntax Error in 3Scale applications response")
        raise

    application_objects = root.findall("application")
    application_list = []
    for application_object in application_objects:
        plan = application_object.find("plan").find("id").text
        if plan == free_plan:
            application_id = application_object.find("id").text
            application_list.append(application_id)
            print("Info: Found application in free plan " + application_id)

    if not application_list:
        return None
    else:
        return application_list


def change_application_plan(account_id, application_id, plan_id, provider_key, api_endpoint):
    """Sends a request to 3scale to change an application's plan.

    :param str account_id: The 3Scale Customer Account ID.
    :param str application_id: The 3Scale Application ID.
    :param str plan_id: The 3Scale Plan ID to change to.
    :param str provider_key: The 3Scale Provider Key
    :param str api_endpoint: The 3Scale API Endpoint

    :return: None
    :rtype: NoneType
    """

    print("Info: Changing application " + application_id + " for account " + account_id + " to plan " + plan_id)

    try:
        r = requests.put('https://' + api_endpoint + '/admin/api/accounts/' + account_id + '/applications/' +
                         application_id + '/change_plan.xml', data={'provider_key': provider_key, 'plan_id': plan_id},
                         timeout=5)
    except requests.RequestException:
        print("Error: Exception raises while changing application plan for " + application_id)
        raise

    if r.status_code == 200:
        print("Info: Success changing application plan for " + application_id)
    else:
        print("Error: Code " + str(r.status_code) + " while changing application plan for " + application_id)
        raise requests.HTTPError


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--provider_key', required=True, help='A 3Scale Provider Key')
    parser.add_argument('--api_endpoint', required=True, help='A 3Scale API Endpoint e.g. myapp.3scale.net')
    parser.add_argument('--free_plan', required=True, help='The 3Scale Plan ID to change from e.g. 12345678')
    parser.add_argument('--paid_plan', required=True, help='The 3Scale Plan ID to change to e.g. 12345678')

    args = parser.parse_args()

    try:
        xml = get_account_xml(args.provider_key, args.api_endpoint)
        accounts = get_accounts_with_card(xml)

        if not accounts:
            print("Info: No accounts found with card details stored")
        else:
            for account in accounts:
                xml = get_application_xml(account, args.provider_key, args.api_endpoint)
                applications = get_free_plan_applications(xml, args.free_plan)

                if applications:
                    for application in applications:
                        change_application_plan(account, application, args.paid_plan, args.provider_key, args.api_endpoint)
    except (requests.RequestException, etree.XMLSyntaxError):
        exit(1)
