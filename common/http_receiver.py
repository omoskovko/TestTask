from urllib import request
from urllib import parse
from . import utils as common_utils

class SmartRedirectHandler(request.HTTPRedirectHandler):
      i = 0
      def http_error_301(self, req, fp, code, msg, headers):
          result = request.HTTPRedirectHandler.http_error_301(
                   self, req, fp, code, msg, headers)

          result.status = code
          self.i += 1
          return result

      http_error_302 = http_error_301
      http_error_303 = http_error_301
      http_error_307 = http_error_301

class Receive(object):
      def __init__(self, vURL, headers={}):
          self.headers = headers

          url = str(vURL).replace(" ", "")
          if len(url) == 0:
             raise(Exception("URL can't be empty"))

          parsed_url = parse.urlparse(url)
          if not parsed_url.hostname:
             parsed_url = parse.urlparse("http://"+url)
          
          self.url = parsed_url.geturl()
          self.sHandler = SmartRedirectHandler()

      def find_connectable_ip(self):
          parsed_url = parse.urlparse(self.url)
          ip = common_utils.find_connectable_ip(parsed_url.hostname,
                            port=parsed_url.port)
          if not ip:
             raise(Exception("Can't find connectable IP for host %s" % (parsed_url.hostname)))

          return ip

      def setdefaulttimeout(self, timeout):
          request.socket.setdefaulttimeout(timeout)

      def urlopen(self):
          res = {'status': 'OK'}
          req = request.Request(self.url, headers=self.headers)
          opener = request.build_opener(self.sHandler)

          try:
             res['object'] = opener.open(req)
          except Exception as url_err:
             res['object'] = None
             res['status'] = "Can't open URL=%s because of error: %s" % (self.url, str(url_err))

          return res
