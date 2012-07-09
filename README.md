Appfail-Django
==============

Appfail Django Reporting Module

See this page for more information:
http://appfail.net/OtherPlatforms

The REST API for Appfail is documented here:
http://support.appfail.net/kb/rest-api-for-reporting-failures/rest-api-documentation-for-failure-reporting


Status
======

Please do not use this reporting module outside of testing environments


Setup
=====

- Clone the repository into your Django project
- Add 'appfail' to your INSTALLED_APPS
- Amend the default LOGGING variable in your settings.py

```python
# add the appfail handler
'handlers': {
    'appfail': {
        'level': 'ERROR',
        'class': 'appfail.log.AppFailHandler',
    }
},

# enable the appfail logger
'loggers': {
    'django.request': {
        'handlers': ['appfail'],
        'level': 'ERROR',
        'api_key': 'YOUR_API_KEY',
        'propagate': True,
    },
}
```