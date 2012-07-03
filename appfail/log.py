import logging
import traceback
import json
from datetime import datetime

from django.conf import settings
from django.views.debug import ExceptionReporter, get_exception_reporter_filter

# Make sure a NullHandler is available
# This was added in Python 2.7/3.2
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# Make sure that dictConfig is available
# This was added in Python 2.7/3.2
try:
    from logging.config import dictConfig
except ImportError:
    from django.utils.dictconfig import dictConfig

getLogger = logging.getLogger

# Ensure the creation of the Django logger
# with a null handler. This ensures we don't get any
# 'No handlers could be found for logger "django"' messages
logger = getLogger('django')
if not logger.handlers:
    logger.addHandler(NullHandler())

# /end taken from django codebase


class AppFailHandler(logging.Handler):
    """
    An exception log handle that logs errors to AppFail.net
    
    Compatible with the AppFail REST API v1:
    http://support.appfail.net/kb/rest-api-for-reporting-failures/documentation-of-submission-format-version-1
    """
    
    def __init__(self):
        logging.Handler.__init__(self)
    
    def emit(self, record):
        send = {}
        
        if record.exc_info:
            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
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
        send['PostValuePairs'] = ""
        send['QueryValuePairs'] = ""
        send['ServerVariable'] = ""
        send['Cookies'] = ""
        send['UniqueId'] = ""
        send['UserAgent'] = record.request.META.get("HTTP_USER_AGENT")
        send['MachineName'] = ""