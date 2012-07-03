import logging
import traceback

import json
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
    
    def __init__(self, api_key="dYCk5eQl6MK7DlA7c2cLVQ"):
        logging.Handler.__init__(self)
        self.api_key = api_key
    
    def emit(self, record):
        send = {}
    
        if record.exc_info:
            stack_trace = traceback.format_exc(record.exc_info)
        else:
            stack_trace = "No stack trace available"
        
        send['ExceptionType'] = record.getMessage()
        send['StackTrace'] = stack_trace
        send['HttpVerb'] = record.request.method
        send['ReferrerUrl'] = record.request.META.get('HTTP_REFERER')
        send['ExceptionMessage'] = ""
        send['RelativeUrl'] = record.request.build_absolute_uri()
        send['ApplicationType'] = "Python/Django"
        send['OccurrenceTimeUtc'] = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S.%f")
        send['User'] = record.request.user.username
        send['PostValuePairs'] = record.request.POST
        send['QueryValuePairs'] = record.request.GET
        send['ServerVariable'] = record.request.session.items(),
        send['Cookies'] = record.request.COOKIES
        send['UniqueId'] = str(uuid.uuid1())         # check if this is OK
        send['UserAgent'] = record.request.META.get("HTTP_USER_AGENT")
        send['MachineName'] = gethostname()
    
        print json.dumps(send)        