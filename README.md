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

- Check the repository out into your Django project
- Amend the default LOGGING variable in your settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}