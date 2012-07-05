import logging
import traceback

import json
import urllib2
import uuid
from datetime import datetime
from socket import gethostname

from django.conf import settings
from django.views.debug import ExceptionReporter, get_exception_reporter_filter

# Make sure that dictConfig is available
# This was added in Python 2.7/3.2
try:
    from logging.config import dictConfig
except ImportError:
    from django.utils.dictconfig import dictConfig

getLogger = logging.getLogger
# /end taken from django codebase


class AppFailHandler(logging.Handler):
    """
    An exception log handle that logs errors to AppFail.net
    
    Compatible with the AppFail REST API v1:
    http://support.appfail.net/kb/rest-api-for-reporting-failures/documentation-of-submission-format-version-1
    """
    
    def __init__(self, api_key="dYCk5eQl6MK7DlA7c2cLVQ", api_url="https://appfail.net/Fail"):
        logging.Handler.__init__(self)
        self.api_key = api_key
        self.api_url = api_url
    
    def emit(self, record):
        occurrence = {}
    
        if record.exc_info:
            stack_trace = traceback.format_exc(record.exc_info)
        else:
            stack_trace = "No stack trace available"
        
        occurrence['ExceptionType'] = record.getMessage()
        occurrence['StackTrace'] = stack_trace
        occurrence['HttpVerb'] = record.request.method
        occurrence['ReferrerUrl'] = record.request.META.get('HTTP_REFERER')
        occurrence['ExceptionMessage'] = ""
        occurrence['RelativeUrl'] = record.request.build_absolute_uri()
        
        # ApplicationType must be set to ASP.NET to be accepted by the server
        occurrence['ApplicationType'] = "Django"         # change to Django on deploy
        
        occurrence['OccurrenceTimeUtc'] = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S.%f")
        occurrence['User'] = record.request.user.username
        occurrence['PostValuePairs'] = record.request.POST
        occurrence['QueryValuePairs'] = record.request.GET
        occurrence['ServerVariable'] = record.request.session.items()
        occurrence['Cookies'] = record.request.COOKIES
        occurrence['UniqueId'] = str(uuid.uuid1())         # check if this is OK
        occurrence['UserAgent'] = record.request.META.get("HTTP_USER_AGENT")
        occurrence['MachineName'] = gethostname()
        
        data = {}
        data['ApiToken'] = self.api_key
        data['FailureOccurrences'] = [occurrence]
        
        print json.dumps(data)
        
        #req = urllib2.Request(self.api_url, json.dumps(data), {'Content-Type': 'application/json', "x-appfail-version": "1"})
        #f = urllib2.urlopen(req)
        #res = f.read()
        #f.close()
        
        #print res