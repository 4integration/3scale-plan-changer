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
from datetime import datetime, timezone


def get_account_list(provider_key, api_endpoint):
    """Downloads the list of approved customer accounts from 3Scale for our provider key and api endpoint and returns
    the XML as a string. May return None if we get an error code from 3Scale.

    :param str provider_key: The 3Scale Provider Key
    :param str api_endpoint: The 3Scale API Endpoint

    :return: Customer account XML element list
    :rtype str or None
    """

    page = 1
    account_objects = []
    while True:
        try:
            r = requests.get('https://' + api_endpoint + '/admin/api/accounts.xml?provider_key=' + provider_key +
                             '&state=approved&page=' + str(page), timeout=30)
        except requests.RequestException as e:
            print("Error: Exception raised while getting account xml from 3scale " + str(e))
            raise

        if r.status_code != 200:
            print("Error: Code " + str(r.status_code) + " while getting account xml from 3scale")
            raise requests.HTTPError

        try:
            root = etree.fromstring(r.text.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            print("Error: XML Syntax Error in 3Scale accounts response " + str(e))
            raise

        account_objects = account_objects + root.findall("account")

        if int(root.attrib['total_pages']) > page:
            page += 1
        else:
            break

    if len(account_objects) == 0:
        raise etree.XMLSyntaxError("No Account Elements in 3Scale XML")
    else:
        print("Got {} accounts back from 3Scale".format(len(account_objects)))

    return account_objects


def get_accounts(account_object_list, card=True):
    """Processes the 3Scale list of customer accounts and returns the id for any that have credit cards stored.

    :param list[xml_element] account_object_list: A list of the 3Scale account XML elements.
    :param bool card: Whether to return accounts with or without a card

    :return: List of 3Scale account ids.
    :rtype: list[tuple]
    """
    accounts_with_card = []
    accounts_without_card = []

    for account_object in account_object_list:
        account_id = account_object.find("id").text
        created_text = account_object.find("created_at").text
        credit_card_status = account_object.find("credit_card_stored").text

        # 3Scale has a colon in their timezone, Python datetime can't deal with that. So this is a bit of a hack
        # to remove the colon character before generating a datetime.
        created_date = datetime.strptime(created_text[:22] + created_text[23:], '%Y-%m-%dT%H:%M:%S%z')

        if credit_card_status == "true":
            accounts_with_card.append(tuple((account_id, created_date)))
        else:
            accounts_without_card.append(tuple((account_id, created_date)))

    print("{} accounts have a card and {} do not".format(len(accounts_with_card), len(accounts_without_card)))

    # If the card param is True then return the list with accounts with cards
    # If not then return the list with accounts with no cards
    if card:
        return accounts_with_card
    else:
        return accounts_without_card


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
                         '/applications.xml?provider_key=' + provider_key, timeout=30)
    except requests.RequestException as e:
        print("Error: Exception raised while getting application xml for account " + account_id + " " + str(e))
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
    except etree.XMLSyntaxError as e:
        print("Error: XML Syntax Error in 3Scale applications response " + str(e))
        raise

    application_objects = root.findall("application")
    application_list = []
    for application_object in application_objects:
        plan = application_object.find("plan").find("id").text
        if plan == free_plan:
            application_id = application_object.find("id").text
            application_name = application_object.find("name").text
            application_list.append(application_id)
            print("Info: Found application in free plan {} with id {}".format(application_name, application_id))

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

    # Make sure the application isn't suspended
    resume_application(account_id, application_id, provider_key, api_endpoint)

    print("Info: Changing application " + application_id + " for account " + account_id + " to plan " + plan_id)

    try:
        r = requests.put('https://' + api_endpoint + '/admin/api/accounts/' + account_id + '/applications/' +
                         application_id + '/change_plan.xml', data={'provider_key': provider_key, 'plan_id': plan_id},
                         timeout=30)
    except requests.RequestException as e:
        print("Error: Exception raised while changing application plan for " + application_id + " " + str(e))
        raise

    if r.status_code == 200:
        print("Info: Success changing application plan for " + application_id)
    else:
        print("Error: Code " + str(r.status_code) + " while changing application plan for " + application_id)
        raise requests.HTTPError


def suspend_application(account_id, application_id, provider_key, api_endpoint):
    """Sends a request to 3scale to suspend an application.

    :param str account_id: The 3Scale Customer Account ID.
    :param str application_id: The 3Scale Application ID.
    :param str provider_key: The 3Scale Provider Key
    :param str api_endpoint: The 3Scale API Endpoint

    :return: None
    :rtype: NoneType
    """

    print("Info: Suspending application " + application_id + " for account " + account_id)

    try:
        r = requests.put('https://' + api_endpoint + '/admin/api/accounts/' + account_id + '/applications/' +
                         application_id + '/suspend.xml', data={'provider_key': provider_key}, timeout=30)
    except requests.RequestException as e:
        print("Error: Exception raised while suspending application " + application_id + " " + str(e))
        raise

    if r.status_code == 200:
        print("Info: Success suspending application " + application_id)
    else:
        print("Error: Code " + str(r.status_code) + " while suspending application " + application_id)
        raise requests.HTTPError


def resume_application(account_id, application_id, provider_key, api_endpoint):
    """Sends a request to 3scale to resume an application.

    :param str account_id: The 3Scale Customer Account ID.
    :param str application_id: The 3Scale Application ID.
    :param str provider_key: The 3Scale Provider Key
    :param str api_endpoint: The 3Scale API Endpoint

    :return: None
    :rtype: NoneType
    """

    print("Info: Resuming application " + application_id + " for account " + account_id)

    try:
        r = requests.put('https://' + api_endpoint + '/admin/api/accounts/' + account_id + '/applications/' +
                         application_id + '/resume.xml', data={'provider_key': provider_key}, timeout=30)
    except requests.RequestException as e:
        print("Error: Exception raised while resuming application " + application_id + " " + str(e))
        raise

    if r.status_code == 200:
        print("Info: Success resuming application " + application_id)
    else:
        print("Error: Code " + str(r.status_code) + " while resuming application " + application_id)
        raise requests.HTTPError


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--provider_key', required=True, help='A 3Scale Provider Key')
    parser.add_argument('--api_endpoint', required=True, help='A 3Scale API Endpoint e.g. myapp.3scale.net')
    parser.add_argument('--free_plan', required=True, help='The 3Scale Plan ID to change from e.g. 12345678')
    parser.add_argument('--paid_plan', required=True, help='The 3Scale Plan ID to change to e.g. 12345678')
    parser.add_argument('--trial_length', required=False, help='How many days to give free accounts before disabling')

    args = parser.parse_args()

    # Get applications with card details and put them on the paid plan
    try:
        accounts_list = get_account_list(args.provider_key, args.api_endpoint)
        accounts_with_card = get_accounts(accounts_list, card=True)
    except (requests.RequestException, etree.XMLSyntaxError) as e:
        print(str(e))
        exit(1)

    try:
        if not accounts_with_card:
            print("Info: No accounts found with card details stored")
        else:
            for account in accounts_with_card:
                xml = get_application_xml(account[0], args.provider_key, args.api_endpoint)
                applications = get_free_plan_applications(xml, args.free_plan)

                if applications:
                    for application in applications:
                        change_application_plan(account[0], application, args.paid_plan, args.provider_key,
                                                args.api_endpoint)
    except requests.RequestException as e:
        print(str(e))
        exit(1)

    # Optionally applications without card details and suspend them if the account is more than {trial_length}
    if not args.trial_length:
        exit(0)

    try:
        accounts_without_card = get_accounts(accounts_list, card=False)
    except etree.XMLSyntaxError as e:
        print(str(e))
        exit(1)

    try:
        if not accounts_without_card:
            print("Info: No accounts found without card details stored")
        else:
            for account in accounts_without_card:
                now = datetime.now(timezone.utc)
                account_created = account[1]
                age = now - account_created
                age_in_days = age.total_seconds()/86400

                if age_in_days > int(args.trial_length):
                    xml = get_application_xml(account[0], args.provider_key, args.api_endpoint)
                    applications = get_free_plan_applications(xml, args.free_plan)

                    if applications:
                        for application in applications:
                            suspend_application(account[0], application, args.provider_key, args.api_endpoint)

    except requests.RequestException as e:
        print(str(e))
        exit(1)
