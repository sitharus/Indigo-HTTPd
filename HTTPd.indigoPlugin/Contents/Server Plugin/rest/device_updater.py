import indigo
import json
import logging
from formatters.format import format_device
from route_handler import RouteHandler
from updaters.update import update

class DeviceUpdater(RouteHandler):
    def __init__(self):
        super(DeviceUpdater, self).__init__('/devices/(\d+)')
        self.logger = logging.getLogger("Plugin.DeviceUpdater")

    def handle_post(self, http_handler, route_matches):
        device = indigo.devices[int(route_matches.group(1))]
        self.logger.debug("Updater found device %s", device.id)
        post_data = http_handler.rfile.read(int(http_handler.headers.getheader('Content-Length')))
        data = json.loads(post_data)
        self.logger.debug("Updating device %s with %s", device.id, data)
        update(device, data)

        device = indigo.devices[device.id]

        http_handler.send_response(200)
        http_handler.send_header("Content-type", "application/json")
        http_handler.end_headers()
        http_handler.wfile.write(json.dumps(format_device(device), sort_keys=True, indent=4, separators=(',', ': ')))
        http_handler.wfile.write("\n")
        return True

