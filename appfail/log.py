import logging
import traceback

import json
import urllib2
import uuid
from datetime import datetime
from socket import gethostname

from django.views.debug import ExceptionReporter, get_exception_reporter_filter
from appfail.models import CachedOccurrence

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
    
    def __init__(self, api_key="dYCk5eQl6MK7DlA7c2cLVQ", api_url="https://api.appfail.net/Fail", verbose=False):
        logging.Handler.__init__(self)
        self.api_key = api_key
        self.api_url = api_url
        self.verbose = verbose
    
    def emit(self, record):
        occurrence = {}
    
        if record.exc_info:
            stack_trace = traceback.format_exc(record.exc_info)
            exception_type = record.exc_info[0].__name__
        else:
            stack_trace = "No stack trace available"
            exception_type = "PageNotFoundException"
        
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
        
        occurrence['PostValuePairs'] = record.request.POST.items()
        occurrence['QueryValuePairs'] = record.request.GET.items()
        occurrence['ServerVariable'] = record.request.session.items()
        
        occurrence['Cookies'] = record.request.COOKIES.items()
        occurrence['UniqueId'] = str(uuid.uuid1()) 
        occurrence['UserAgent'] = record.request.META.get("HTTP_USER_AGENT")
        occurrence['MachineName'] = gethostname()
        
        # ok, add this to the database as a new CachedOccurrence object
        co = CachedOccurrence()
        co.failure_json = json.dumps(occurrence)
        co.reported = False
        
        
        
        data = {}
        data['ApiToken'] = self.api_key
        data['ApplicationType'] = "Django"          # ApplicationType for Python has been added
        data['ModuleVersion'] = "0.0.0.1"
        data['FailOccurrences'] = [occurrences]
        
        req = urllib2.Request(self.api_url, data=json.dumps(data), headers = {
                "content-type": "application/json", 
                "x-appfail-version": 2,
                "user-agent": "AppFail Django Reporting Module/0.1"
            })
        
        
        if self.verbose:
            print "SENDING JSON"
            print "URL: ", self.api_url
            print json.dumps(data, sort_keys=True, indent=4)
            print "\n--------------------------------------------------"
            
        if "favicon" not in occurrence['RequestUrl']:
            try:
                f = urllib2.urlopen(req)
                res = f.read()
                f.close()
            
                if self.verbose:
                    print "Our header: %s" % req.header_items()
                    print "Server response: %s:" % f.info()
                    print res
            
            except urllib2.HTTPError, e:
                print "SERVER ERROR:"
                print str(e)
                print e.read()
                print "\n--------------------------------------------------"