3Scale Application Approver [![Build Status](https://travis-ci.org/cablespaghetti/3scale-application-approver.svg?branch=master)](https://travis-ci.org/cablespaghetti/3scale-application-approver)

============

A simple app that uses the 3Scale API to Accept applications that are Pending but their account has credit card information stored.

Requirements
============

* Python 3
* lxml
* requests

Usage
=====
```
python3 approver.py --provider_key=my-3scale-provider-key --api_endpoint=myapp.3scale.net
```

