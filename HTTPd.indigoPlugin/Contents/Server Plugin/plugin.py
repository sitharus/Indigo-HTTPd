#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################

import sys
import time
import os
import base64
import logging

from ghpu import GitHubPluginUpdater

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs

########################################

def updateVar(name, value, folder):
    if name not in indigo.variables:
        indigo.variable.create(name, value=value, folder=folder)
    else:
        indigo.variable.updateValue(name, value)

########################################
class MyHTTPServer(HTTPServer):

    def setKey(self, authKey):
        self.authKey = authKey


class AuthHandler(BaseHTTPRequestHandler):

#    def log_message(self, format, *args):
#        self.logger = logging.getLogger("Plugin.AuthHandler")
#        self.logger.debug("AuthHandler Message: " + format % args)
#        return

    def do_HEAD(self):
        self.logger = logging.getLogger("Plugin.AuthHandler")
        self.logger.debug('AuthHandler: do_HEAD')

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        self.logger = logging.getLogger("Plugin.AuthHandler")
        self.logger.debug("AuthHandler: do_POST")

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        auth_header = self.headers.getheader('Authorization')

    def do_GET(self):
        self.logger = logging.getLogger("Plugin.AuthHandler")

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        auth_header = self.headers.getheader('Authorization')

        if auth_header == None:
            self.logger.debug("AuthHandler: do_GET with no Authorization header")
            self.wfile.write("<html>\n<head><title>Indigo HTTPd Plugin</title></head>\n<body>")
            self.wfile.write("\n<p>Basic Authentication Required</p>")
            self.wfile.write("\n</body>\n</html>\n")

        elif auth_header == ('Basic ' + self.server.authKey):
            self.logger.debug(u"AuthHandler: authorized do_GET: %s" % self.path)
            self.wfile.write("<html>\n<head><title>Indigo HTTPd Plugin</title></head>\n<body>")
            request = urlparse(self.path)

            if request.path == "/setvar":
                query = parse_qs(request.query)
                for key in query:
                    self.logger.debug(u"AuthHandler: setting variable httpd_%s to %s" % (key, query[key][0]))
                    updateVar("httpd_"+key, query[key][0], indigo.activePlugin.pluginPrefs["folderId"])
                    self.wfile.write("\n<p>Updated variable %s</p>" % key)

                indigo.activePlugin.triggerCheck()

            else:
                self.logger.debug(u"AuthHandler: do_GET with unknown request: %s" % self.request)

            self.wfile.write("\n</body>\n</html>\n")

        else:
            self.logger.debug(u"AuthHandler: do_GET with invalid Authorization header")
            self.wfile.write("<html>\n<head><title>Indigo HTTPd Plugin</title></head>\n<body>")
            self.wfile.write("\n<p>Invalid Authentication</p>")
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

