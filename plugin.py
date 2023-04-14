########################################################################################
# 	Fronius Inverter Python Plugin for Domoticz                                   	   #
#                                                                                      #
# 	MIT License                                                                        #
#                                                                                      #
#	Copyright (c) 2018 ADJ                                                             #
#                                                                                      #
#	Permission is hereby granted, free of charge, to any person obtaining a copy       #
#	of this software and associated documentation files (the "Software"), to deal      #
#	in the Software without restriction, including without limitation the rights       #
#	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell          #
#	copies of the Software, and to permit persons to whom the Software is              #
#	furnished to do so, subject to the following conditions:                           #
#                                                                                      #
#	The above copyright notice and this permission notice shall be included in all     #
#	copies or substantial portions of the Software.                                    #
#                                                                                      #
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR         #
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,           #
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE        #
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER             #
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,      #
#	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE      #
#	SOFTWARE.                                                                          #
#                                                                                      #
#   Author: ADJ / sincze                                                               #
#                                                                                      #
#   This plugin will read the status from the running inverter via the webservice.     #
#                                                                                      #
#   V 0.0.1. ADJ Initial Release (2018),                                               #
#            https://github.com/aukedejong/domoticz-fronius-inverter-plugin.git        #
#   V 0.0.2. S. Incze (14-04-2023),                                                    #            
#            Fix crashing issues during nighttime                                      #
########################################################################################

"0000000000000000000000000000000000000000000000000000000000000000000000""
<plugin key="froniusInverter" name="Fronius Inverter" author="ADJ & SINCZE" version="0.0.2" wikilink="https://github.com/aukedejong/domoticz-fronius-inverter-plugin.git" externallink="http://www.fronius.com">
    <params>
        <param field="Mode1" label="IP Address" required="true" width="200px" />
        <param field="Mode2" label="Device ID" required="true" width="100px" />
        <param field="Mode6" label="Debug" width="100px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
                <option label="Logging" value="File"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import sys
import json
import datetime
import urllib.request
import urllib.error

class BasePlugin:
    inverterWorking = True
    intervalCounter = None
    heartbeat = 30
    totalWh = 0
    currentWatts = 0

    def onStart(self):
        if Parameters["Mode6"] != "Normal":
            Domoticz.Debugging(1)

        if (len(Devices) == 0):
            Domoticz.Device(Name="Current power",  Unit=1, TypeName="Custom", Options = { "Custom" : "1;Watt"}, Used=1).Create()
            Domoticz.Device(Name="Total power",  Unit=2, TypeName="kWh", Used=1).Create()
            logDebugMessage("Devices created.")

        Domoticz.Heartbeat(self.heartbeat)
        self.intervalCounter = 0

        if ('FroniusInverter' not in Images): Domoticz.Image('Fronius Inverter Icons.zip').Create()
        if ('FroniusInverterOff' not in Images): Domoticz.Image('Fronius Inverter Off Icons.zip').Create()

        Devices[1].Update(0, sValue=str(Devices[1].sValue), Image=Images["FroniusInverter"].ID)
        Devices[2].Update(0, sValue=str(Devices[2].sValue), Image=Images["FroniusInverter"].ID)
        return True

    def onHeartbeat(self):
        if self.intervalCounter == 1:
            ipAddress = Parameters["Mode1"]
            deviceId = Parameters["Mode2"]
            jsonObject = self.getInverterRealtimeData( ipAddress, deviceId )

            if (self.isInverterActive(jsonObject)):

                self.updateDeviceCurrent(jsonObject)
                self.updateDeviceMeter(jsonObject)

                if (self.inverterWorking == False):
                    self.inverterWorking = True

            else:
                self.logErrorCode(jsonObject)
                self.logErrorCode2(jsonObject)

                if (self.inverterWorking == True):
                    self.inverterWorking = False
                    self.updateDeviceOff()

            self.intervalCounter = 0

        else:
            self.intervalCounter = 1
            logDebugMessage("Do nothing: " + str(self.intervalCounter))

        return True

    def getInverterRealtimeData(self, ipAddress, deviceId):
        url = "http://" + ipAddress + "/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=" + deviceId + "&DataCollection=CommonInverterData"
        logDebugMessage('Retrieve solar data from ' + url)

        try:
            req = urllib.request.Request(url)
            jsonData = urllib.request.urlopen(req).read()
            jsonObject = json.loads(jsonData.decode('utf-8'))
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logErrorMessage("Error: " + str(e) + " URL: " + url)
            return

        logDebugMessage("JSON: " + str(jsonData))

        return jsonObject

    def isInverterActive(self, jsonObject):
        try:
            logDebugMessage("Debug isInverterActive: " + json.dumps(jsonObject))
            if (jsonObject["Head"]["Status"]["Code"] == 0):                         # When JSON returns during night
                logDebugMessage("isInverterActive: True")
                return True
            else:
                logDebugMessage("isInverterActive: False")
                return False
        except:
            logErrorMessage("Error isInverterActive: Inverter is not Active")
            return False

    def logErrorCode(self, jsonObject):
        try:
            code = jsonObject["Head"]["Status"]["Code"]
            reason = jsonObject["Head"]["Status"]["Reason"]

            if (code != 12):
               logErrorMessage("Code: " + str(code) + ", reason: " + reason  )
            return
        except:
            logErrorMessage("logErrorCode Status Code does not Exist: " + json.dumps(jsonObject))
            return

    def logErrorCode2(self, jsonObject):
        try:
            code = jsonObject["Body"]["Data"]["DeviceStatus"]["ErrorCode"]

            if (code != 12):
               logErrorMessage("logErrorCode2 Code: " + str(code) )
            return
        except:
            logErrorMessage("logErrorCode2 Status Code does not Exist: " + json.dumps(jsonObject))
            return

    def updateDeviceCurrent(self, jsonObject):
        try:
            currentWatts = jsonObject["Body"]["Data"]["PAC"]["Value"]
            Devices[1].Update(currentWatts, str(currentWatts), Images["FroniusInverter"].ID)
            self.currentWatts = currentWatts
            return
        except KeyError:
            self.currentWatts = 0
            logErrorMessage("updateDeviceCurrent value not available: " + json.dumps(jsonObject))
            return

    def updateDeviceMeter(self, jsonObject):
        try:
            totalWh = jsonObject["Body"]["Data"]["TOTAL_ENERGY"]["Value"]
            #currentWatts = jsonObject["Body"]["Data"]["PAC"]["Value"]
            currentWatts = self.currentWatts
            Devices[2].Update(0, str(currentWatts) + ";" + str(totalWh))
            self.totalWh = totalWh
            return
        except KeyError:
            logErrorMessage("updateDeviceMeter value not available: " + json.dumps(jsonObject))
            return

    def updateDeviceOff(self):
        try:
            Devices[1].Update(0, "0", Images["FroniusInverterOff"].ID)
            totalWh = self.totalWh
            Devices[2].Update(0, "0;" + str(totalWh))
            return
        except KeyError:
            logErrorMessage("updateDeviceOff value not available: ")
            return

    def onStop(self):
        logDebugMessage("onStop called")
        return True

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def logDebugMessage(message):
    if (Parameters["Mode6"] == "Debug"):
        now = datetime.datetime.now()
        f = open(Parameters["HomeFolder"] + "fronius-inverter-plugin.log", "a")
        f.write("DEBUG - " + now.isoformat() + " - " + message + "\r\n")
        f.close()
    Domoticz.Debug(message)

def logErrorMessage(message):
    if (Parameters["Mode6"] == "Debug"):
        now = datetime.datetime.now()
        f = open(Parameters["HomeFolder"] + "fronius-inverter-plugin.log", "a")
        f.write("ERROR - " + now.isoformat() + " - " + message + "\r\n")
        f.close()
    Domoticz.Error(message)
