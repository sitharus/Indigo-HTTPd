import indigo
import json
from formatters.format import format_device
from route_handler import RouteHandler

class Devices(RouteHandler):
    def __init__(self):
        super(Devices, self).__init__('/devices')

    def handle_get(self, http_handler, route_matches):
        prefs = http_handler.server.plugin_prefs
        device_descriptions = [format_device(d, prefs) for d in indigo.devices]

        http_handler.send_response(200)
        http_handler.send_header("Content-type", "application/json")
        http_handler.end_headers()
        http_handler.wfile.write(json.dumps(device_descriptions, sort_keys=True, indent=4, separators=(',', ': ')))
        http_handler.wfile.write("\n")
        return True

