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
    
    def __init__(self, api_key="dYCk5eQl6MK7DlA7c2cLVQ", api_url="https://api.appfail.net/Fail"):
        logging.Handler.__init__(self)
        self.api_key = api_key
        self.api_url = api_url
    
    def emit(self, record):
        occurrence = {}
    
        if record.exc_info:
            stack_trace = traceback.format_exc(record.exc_info)
            exception_type = record.exc_info[0].__name__
        else:
            stack_trace = "No stack trace available"
            exception_type = "PageNotFoundException"
        
        """
        API Version 1
        
        occurrence['ExceptionType'] = record.getMessage()
        occurrence['StackTrace'] = stack_trace
        occurrence['HttpVerb'] = record.request.method
        occurrence['ReferrerUrl'] = record.request.META.get('HTTP_REFERER')
        occurrence['ExceptionMessage'] = ""
        occurrence['RelativeUrl'] = record.request.build_absolute_uri()
        occurrence['OccurrenceTimeUtc'] = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S.%f")
        occurrence['User'] = record.request.user.username
        occurrence['PostValuePairs'] = record.request.POST
        occurrence['QueryValuePairs'] = record.request.GET
        occurrence['ServerVariable'] = record.request.session.items()
        occurrence['Cookies'] = record.request.COOKIES
        occurrence['UniqueId'] = str(uuid.uuid1())         # check if this is OK
        occurrence['UserAgent'] = record.request.META.get("HTTP_USER_AGENT")
        occurrence['MachineName'] = gethostname()
        """
        
        """
        API Version 2
        """
        exception = {}
        exception['ExceptionType'] = exception_type
        exception['ExceptionMessage'] = record.getMessage()
        exception['StackTrace'] = stack_trace
        
        occurrence['Exceptions'] = [exception]
        occurrence['HttpVerb'] = record.request.method
        occurrence['HttpStatus'] = None
        occurrence['RequestUrl'] = record.request.build_absolute_uri()
        occurrence['ReferrerUrl'] = record.request.META.get('HTTP_REFERER', '')
        occurrence['OccurrenceTimeUtc'] = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S.%f")
        occurrence['User'] = record.request.user.username
        #occurrence['PostValuePairs'] = record.request.POST.items()
        #occurrence['QueryValuePairs'] = record.request.GET.items()
        #occurrence['ServerVariable'] = record.request.session.items()
        
        occurrence['PostValuePairs'] = [['name','value']]
        occurrence['QueryValuePairs'] = [['name','value']]
        occurrence['ServerVariables'] = [['name','value']]
        
        occurrence['Cookies'] = record.request.COOKIES.items()
        occurrence['UniqueId'] = str(uuid.uuid1()) 
        occurrence['UserAgent'] = record.request.META.get("HTTP_USER_AGENT")
        occurrence['MachineName'] = gethostname()
        
        
        data = {}
        data['ApiToken'] = self.api_key
        
        data['ApplicationType'] = "Python"          # ApplicationType for Django has been added
        data['ModuleVersion'] = "0.0.0.1"
        data['FailureOccurrences'] = [occurrence]
        
        print json.dumps(data, sort_keys=True, indent=4)
        print self.api_url
        
        if "favicon" not in exception['ExceptionMessage']:
            req = urllib2.Request(self.api_url, data=json.dumps(data), 
                headers={
                    'Content-Type': 'application/json', 
                    "x-appfail-version": "2",
                    "User-Agent": "AppFail Django Reporting Module/0.1"
                })
        
        
            print req.header_items()
            f = urllib2.urlopen(req)
            print f.info()
            res = f.read()
            f.close()
        
            print res
        