import re
import logging
from urlparse import urlparse

class RestHandler(object):
    def __init__(self):
        self.handlers = [Devices()]
        self.logger = logging.getLogger("Plugin.AuthHandler")

    def process_get(self, http_handler):
        try:
            request_url = urlparse(http_handler.path)
            for handler in self.handlers:
                match = handler.handles(request_url.path)
                if match:
                    return handler.handle_get(http_handler, match)
            return None
        except Exception as e:
            self.logger.debug("Caught exception searching for routes %s", e)
            return None

class RouteHandler(object):
    def __init__(self, route):
        self.route = route

    def handles(self, url):
        return re.match("^%s$" % (self.route), url)

    def handle_get(self, http_handler, route_matches):
        return None

    def handle_post(self, http_handler, route_matches):
        return None

class Devices(RouteHandler):
    def __init__(self):
        super(Devices, self).__init__('/devices')

    def handle_get(self, http_handler, route_matches):
        http_handler.send_response(200)
        http_handler.send_header("Content-type", "text/plain")
        http_handler.end_headers()
        http_handler.wfile.write("test\n")
        return True

