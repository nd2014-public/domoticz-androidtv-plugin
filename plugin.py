#           AndroidTV Plugin
#
#           Author:     M. Salles, 2019
#

"""
<plugin key="AndroidTVPlugin" name="AndroidTV" author="MSALLES" version="0.0.1" wikilink="https://github.com/nd2014public/domoticz-androidtv-plugin.git">
    <params>
        <param field="Mode1" label="IP address of android tv" required="true" width="200px" />
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
import subprocess
import os 

class BasePlugin:

    def onStart(self):
        if Parameters["Mode6"] != "Normal":
            Domoticz.Debugging(1)

        subprocess.run(["adb", "connect", Parameters["Mode1"]+":5555"])

        if (len(Devices) == 0):

            Domoticz.Device(Name="Running App",  Unit=1, TypeName="Alert").Create()

            logDebugMessage("Devices created.")

        return True

    def onCommand(self, Unit, Command, Level, Color):        
        return True

    def onHeartbeat(self):

        # Get Activity running on AndroidTV :
        result = str(subprocess.check_output("adb shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'", shell=True))

        # Kodi ? Which media ?
        # YouTube ? Which video ?
        # TV ? Which channel / program ?
        # Other app ? Which one ?
        running_app = 'Other app'
        if (result.find('com.android.tv.MainActivity') > -1):
            running_app = "TV"
        elif (result.find('fr.freebox.catchupstore') > -1):
            running_app = "Freebox Replay"
        elif (result.find('org.xbmc.kodi') > -1):
            running_app = "Kodi"
        elif (result.find('youtube.tvkids') > -1):
            running_app = "YouTube Kids"
        elif (result.find('com.google.android.youtube.tv') > -1):
            running_app = "YouTube"
        elif (result.find('tv.molotov.app') > -1):
            running_app = "Molotov"
        elif (result.find('com.canal.android.canal') > -1):
            running_app = "MyCanal"
        elif (result.find('com.orange.ocsgo') > -1):
            running_app = "OCS"
        elif (result.find('leanbacklauncher.MainActivity') > -1):
            running_app = "AndroidTV Off / SplashScreen"
        Devices[1].Update(nValue=1, sValue=str(running_app))

        return True

    def logErrorCode(self, jsonObject):
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

def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def logDebugMessage(message):
    if (Parameters["Mode6"] == "Debug"):
        now = datetime.datetime.now()
        f = open(Parameters["HomeFolder"] + "androidtv-plugin.log", "a")
        f.write("DEBUG - " + now.isoformat() + " - " + message + "\r\n")
        f.close()
    Domoticz.Debug(message)

def logErrorMessage(message):
    if (Parameters["Mode6"] == "Debug"):
        now = datetime.datetime.now()
        f = open(Parameters["HomeFolder"] + "androidtv-plugin.log", "a")
        f.write("ERROR - " + now.isoformat() + " - " + message + "\r\n")
        f.close()
    Domoticz.Error(message)
