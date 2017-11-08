import logging
from urlparse import urlparse

from devices import Devices
from device_updater import DeviceUpdater

class RestHandler(object):
    def __init__(self):
        self.handlers = [DeviceUpdater(), Devices()]
        self.logger = logging.getLogger("Plugin.AuthHandler")

    def process_get(self, http_handler):
        try:
            handler, match = self.find_handler(http_handler)
            if handler is not None:
                return handler.handle_get(http_handler, match)
        except Exception as e:
            self.logger.debug("Caught exception searching for routes %s", e)
            return None
    
    def process_post(self, http_handler):
        try:
            handler, match = self.find_handler(http_handler)
            self.logger.debug("Handling post with %s, matches %s", handler, match)
            if handler is not None:
                return handler.handle_post(http_handler, match)
        except Exception as e:
            self.logger.debug("Caught exception searching for routes %s", e)
            return None

    def process_put(self, http_handler):
        try:
            handler, match = self.find_handler(http_handler)
            self.logger.debug("Handling put with %s, matches %s", handler, match)
            if handler is not None:
                return handler.handle_put(http_handler, match)
        except Exception as e:
            self.logger.debug("Caught exception searching for routes %s", e)
            return None
    
    def find_handler(self, http_handler):
        request_url = urlparse(http_handler.path)
        for handler in self.handlers:
            match = handler.handles(request_url.path)
            if match:
                return handler, match
        return None, None


