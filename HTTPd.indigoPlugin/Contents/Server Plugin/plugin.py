#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################

import sys
import time
import os
import base64
import logging
import indigo

from ghpu import GitHubPluginUpdater

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs
from rest.rest import RestHandler

# taken from http://www.piware.de/2011/01/creating-an-https-server-in-python/
# generate server.xml with the following command:
#    openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# run as follows:
#    python simple-https-server.py
# then in your browser, visit:
#    https://localhost:4443
#import BaseHTTPServer, SimpleHTTPServer
#import ssl
#httpd = BaseHTTPServer.HTTPServer(('localhost', 4443), SimpleHTTPServer.SimpleHTTPRequestHandler)
#httpd.socket = ssl.wrap_socket (httpd.socket, certfile='./server.pem', server_side=True)
#httpd.serve_forever()


########################################

def updateVar(name, value, folder):
    if name not in indigo.variables:
        indigo.variable.create(name, value=value, folder=folder)
    else:
        indigo.variable.updateValue(name, value)

########################################
class MyHTTPServer(HTTPServer):
    def __init__(self, listen, handler):
        HTTPServer.__init__(self, listen, handler)
        logging.getLogger("Plugin.HttpServer").debug("Starting custom HTTP server on %s with %s", listen, handler)
        self.authKey = ""

    def setKey(self, authKey):
        self.authKey = authKey

class AuthHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger("Plugin.AuthHandler")
        self.rest_handler = RestHandler()
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_POST(self):
        client_host, client_port = self.client_address
        self.logger.debug("AuthHandler: POST from %s:%s to %s", str(client_host), str(client_port), self.path)

        auth_header = self.headers.getheader('Authorization')
        if auth_header == ('Basic ' + self.server.authKey):
            self.logger.debug("AuthHandler: handling request to %s", self.path)
            self.rest_handler.process_post(self)
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("URL not found\n")

    def do_PUT(self):
        client_host, client_port = self.client_address
        self.logger.debug("AuthHandler: PUT from %s:%s to %s", str(client_host), str(client_port), self.path)

        auth_header = self.headers.getheader('Authorization')
        if auth_header == ('Basic ' + self.server.authKey):
            self.logger.debug("AuthHandler: handling request to %s", self.path)
            self.rest_handler.process_put(self)
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("URL not found\n")

    def do_GET(self):
        client_host, client_port = self.client_address
        self.logger.debug("AuthHandler: GET from %s:%s for %s", str(client_host), str(client_port), self.path)

        auth_header = self.headers.getheader('Authorization')

        if auth_header is None:
            self.send_response(401)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.logger.debug("AuthHandler: Request has no Authorization header")
            self.wfile.write("<html>\n<head><title>Indigo HTTPd Plugin</title></head>\n<body>")
            self.wfile.write("\n<p>Basic Authentication Required</p>")
            self.wfile.write("\n</body>\n</html>\n")
        elif auth_header == ('Basic ' + self.server.authKey):
            self.logger.debug("AuthHandler: handling request to %s", self.path)
            handled = None
            try:
                handled = self.rest_handler.process_get(self)
            except Exception as e:
                self.logger.debug("Exception in route handling %s", e)
            self.logger.debug("Handled was %s", handled)
            if handled is None:
                self.logger.debug('Route not handled, falling back to setvar')
                self.handle_setvar()
        else:
            self.send_response(401)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.logger.debug(u"AuthHandler: Request with invalid Authorization header")
            self.wfile.write("<html>\n<head><title>Indigo HTTPd Plugin</title></head>\n<body>")
            self.wfile.write("\n<p>Invalid Authentication</p>")
            self.wfile.write("\n</body>\n</html>\n")

    def handle_setvar(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.logger.debug(u"AuthHandler: Request has correct Authorization header")
        self.wfile.write("<html>\n<head><title>Indigo HTTPd Plugin</title></head>\n<body>")
        request = urlparse(self.path)

        if request.path == "/setvar":
            query = parse_qs(request.query)
            for key in query:
                self.logger.debug(u"AuthHandler: setting variable httpd_%s to %s", key, query[key][0])
                updateVar("httpd_"+key, query[key][0], indigo.activePlugin.pluginPrefs["folderId"])
                self.wfile.write("\n<p>Updated variable %s</p>" % key)
            indigo.activePlugin.triggerCheck()

        else:
            self.logger.debug(u"AuthHandler: Unknown request: %s", self.path)
        self.wfile.write("\n</body>\n</html>\n")



class Plugin(indigo.PluginBase):

    ########################################
    # Main Plugin methods
    ########################################
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        pfmt = logging.Formatter('%(asctime)s.%(msecs)03d\t[%(levelname)8s] %(name)20s.%(funcName)-25s%(msg)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.plugin_file_handler.setFormatter(pfmt)

        try:
            self.logLevel = int(self.pluginPrefs[u"logLevel"])
        except:
            self.logLevel = logging.INFO
        self.indigo_log_handler.setLevel(self.logLevel)
        self.logger.debug(u"logLevel = " + str(self.logLevel))


    def startup(self):
        indigo.server.log(u"Starting HTTPd")

        self.updater = GitHubPluginUpdater(self)
        self.updateFrequency = float(self.pluginPrefs.get('updateFrequency', '24')) * 60.0 * 60.0
        self.next_update_check = time.time()

        user = self.pluginPrefs.get('httpUser', 'username')
        password = self.pluginPrefs.get('httpPassword', 'password')
        self.authKey = base64.b64encode(user + ":" + password)

        self.port = int(self.pluginPrefs.get('httpPort', '5555'))

        if "HTTPd" in indigo.variables.folders:
            myFolder = indigo.variables.folders["HTTPd"]
        else:
            myFolder = indigo.variables.folder.create("HTTPd")
        self.pluginPrefs["folderId"] = myFolder.id

        self.triggers = {}

        self.logger.debug(u"Starting HTTP server on port %d" % self.port)
        try:
            self.httpd = MyHTTPServer(("", self.port), AuthHandler)
        except:
            self.logger.error(u"Unable to open port %d for HHTTP Server" % self.port)
            self.httpd = None
        else:
            self.httpd.timeout = 1.0
            self.httpd.setKey(self.authKey)



    def shutdown(self):
        indigo.server.log(u"Shutting down HTTPd")


    def runConcurrentThread(self):

        try:
            while True:
                self.httpd.handle_request()

                if (self.updateFrequency > 0.0) and (time.time() > self.next_update_check):
                    self.next_update_check = time.time() + self.updateFrequency
                    self.updater.checkForUpdate()

                self.sleep(0.1)

        except self.StopThread:
            pass


    ####################

    def triggerStartProcessing(self, trigger):
        self.logger.debug("Adding Trigger %s (%d) - %s" % (trigger.name, trigger.id, trigger.pluginTypeId))
        assert trigger.id not in self.triggers
        self.triggers[trigger.id] = trigger

    def triggerStopProcessing(self, trigger):
        self.logger.debug("Removing Trigger %s (%d)" % (trigger.name, trigger.id))
        assert trigger.id in self.triggers
        del self.triggers[trigger.id]

    def triggerCheck(self):
        for triggerId, trigger in sorted(self.triggers.iteritems()):
            self.logger.debug("Checking Trigger %s (%s), Type: %s" % (trigger.name, trigger.id, trigger.pluginTypeId))
            if trigger.pluginTypeId == 'requestReceived':
                indigo.trigger.execute(trigger)


    ####################
    def validatePrefsConfigUi(self, valuesDict):
        self.logger.debug(u"validatePrefsConfigUi called")
        errorDict = indigo.Dict()

        updateFrequency = int(valuesDict['updateFrequency'])
        if (updateFrequency < 0) or (updateFrequency > 24):
            errorDict['updateFrequency'] = u"Update frequency is invalid - enter a valid number (between 0 and 24)"

        httpPort = int(valuesDict['httpPort'])
        if httpPort < 1024:
            errorDict['httpPort'] = u"HTTP Port Number invalid"

        if len(errorDict) > 0:
            return (False, valuesDict, errorDict)
        return (True, valuesDict)

    ########################################
    def closedPrefsConfigUi(self, valuesDict, userCancelled):
        if not userCancelled:
            try:
                self.logLevel = int(valuesDict[u"logLevel"])
            except:
                self.logLevel = logging.INFO
            self.indigo_log_handler.setLevel(self.logLevel)
            self.logger.debug(u"logLevel = " + str(self.logLevel))

            self.updateFrequency = float(self.pluginPrefs.get('updateFrequency', "24")) * 60.0 * 60.0
            self.logger.debug(u"updateFrequency = " + str(self.updateFrequency))
            self.next_update_check = time.time()


    ########################################
    # Menu Methods
    ########################################

    def checkForUpdates(self):
        self.updater.checkForUpdate()

    def updatePlugin(self):
        self.updater.update()

    def forceUpdate(self):
        self.updater.update(currentVersion='0.0.0')

