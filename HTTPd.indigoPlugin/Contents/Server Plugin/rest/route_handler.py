import re

class RouteHandler(object):
    def __init__(self, route):
        self.route = route

    def handles(self, url):
        return re.match("^%s$" % (self.route), url)

    def handle_get(self, http_handler, route_matches):
        return None

    def handle_post(self, http_handler, route_matches):
        return None
