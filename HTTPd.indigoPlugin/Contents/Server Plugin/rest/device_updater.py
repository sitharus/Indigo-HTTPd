import indigo
import cgi
import json
import logging
from formatters.format import format_device
from route_handler import RouteHandler
from updaters.update import update
from urlparse import urlparse, parse_qs

class DeviceUpdater(RouteHandler):
    def __init__(self):
        super(DeviceUpdater, self).__init__('/devices/(\d+)')
        self.logger = logging.getLogger("Plugin.DeviceUpdater")

    def handle_get(self, http_handler, route_matches):
        prefs = http_handler.server.plugin_prefs
        device = indigo.devices[int(route_matches.group(1))]
        http_handler.send_response(200)
        http_handler.send_header("Content-type", "application/json")
        http_handler.end_headers()
        http_handler.wfile.write(json.dumps(format_device(device, prefs), sort_keys=True, indent=4, separators=(',', ': ')))
        http_handler.wfile.write("\n")
        return True

    def handle_put(self, http_handler, route_matches):
        return self.handle_post(http_handler, route_matches)

    def handle_post(self, http_handler, route_matches):
        prefs = http_handler.server.plugin_prefs
        device = indigo.devices[int(route_matches.group(1))]
        self.logger.debug("Updater found device %s", device.id)
        post_data = http_handler.rfile.read(int(http_handler.headers.getheader('Content-Length')))

        if http_handler.headers.getheader('Content-Type') == 'application/json':
            data = json.loads(post_data)
        elif len(post_data) > 0:
            data = {}
            cgi.parse_multipart(post_data, data)
        else:
            query = urlparse(http_handler.path).query
            data = parse_qs(query)
        self.logger.debug("Updating device %s with %s", device.id, data)
        update(device, data, prefs)

        device = indigo.devices[device.id]

        http_handler.send_response(200)
        http_handler.send_header("Content-type", "application/json")
        http_handler.end_headers()
        http_handler.wfile.write(json.dumps(format_device(device, prefs), sort_keys=True, indent=4, separators=(',', ': ')))
        http_handler.wfile.write("\n")
        return True

