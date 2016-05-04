3Scale Plan Changer [![Build Status](https://travis-ci.org/SnowflakeSoftware/3scale-plan-changer.svg?branch=master)](https://travis-ci.org/SnowflakeSoftware/3scale-plan-changer)
===========================

A simple app that uses the 3Scale API to change application plans when the associated account has credit card information stored.

Requirements
============

* Python 3
* lxml
* requests

Usage
=====
```
python3 changer.py --provider_key=my-3scale-key --api_endpoint=myapp.3scale.net --free_plan=12345 --paid_plan=12345
```

