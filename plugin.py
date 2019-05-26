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
import re

class BasePlugin:

    def onStart(self):
        Domoticz.Heartbeat(60)
        if Parameters["Mode6"] != "Normal":
            Domoticz.Debugging(1)

        subprocess.run(["adb", "connect", Parameters["Mode1"]+":5555"])

        if (len(Devices) == 0):
            Domoticz.Device(Name="Running App",  Unit=1, TypeName="Text").Create()
            Domoticz.Device(Name="Running App Channel",  Unit=2, TypeName="Text").Create()
            Domoticz.Device(Name="Running App Program",  Unit=3, TypeName="Text").Create()
            Domoticz.Device(Name="Running package",  Unit=4, TypeName="Text").Create()

            logDebugMessage("Devices created.")

        return True

    def onCommand(self, Unit, Command, Level, Color):        
        return True

    def onHeartbeat(self):


        # Get wake or asleep :
        wake_state = 'asleep' 
        running_package = 'None'
        running_app = 'TV Off/Asleep'
        running_app_channel = "None"
        running_app_infos = "None"
        result = str(subprocess.check_output("adb shell dumpsys power |grep 'mWakefulness'", shell=True, timeout=10))
        if (result.find('mWakefulness=Awake') > -1):
            wake_state='awake'
            running_app = 'Other app'
        
        # Running package :
        log = str(subprocess.check_output("adb shell dumpsys window windows |grep -E 'mCurrentFocus'", shell=True, timeout=10))
        current_focus = re.search(' (.*)/', log, re.IGNORECASE)
        if (current_focus):
            running_package = current_focus.group(1)
        else:
            running_package = ""
        


        # Get Activity running on AndroidTV :
        result = str(subprocess.check_output("adb shell dumpsys window windows |grep -E 'mCurrentFocus|mFocusedApp'", shell=True, timeout=10))

        # Kodi ? Which media ?
        # YouTube ? Which video ?
        # TV ? Which channel / program ?
        # Other app ? Which one ?
        if (wake_state == 'awake'):

            running_app = "Other app"
            if (result.find('com.android.tv.MainActivity') > -1):
                running_app = "TV"
            elif (result.find('fr.freebox.catchupstore') > -1):
                running_app = "Freebox Replay"
            elif (result.find('fr.freebox.qmllauncher') > -1):
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
                running_app = "SplashScreen"

            if (running_app == "Freebox Replay"):
                log = str(subprocess.check_output("adb logcat -d -t 5000 |grep -E 'vodservice' |tail -n 1", shell=True, timeout=10))
                vod_search = re.search('android.intent.action.VIEW dat=vodservice://(.*) flg=', log, re.IGNORECASE)
                if vod_search:
                    print("VOD found ...", vod_search)
                    running_app_channel = vod_search.group(1)

            elif (running_app == "TV"):
                log = str(subprocess.check_output("adb logcat -d -t 5000 |grep -E 'open rtsp://rtsp-server/fbxtv_priv/stream' |tail -n 1", shell=True, timeout=10))
                service_no = re.search('service=([0-9]+)', log, re.IGNORECASE)
                if (service_no):
                    service_no = service_no.group(1)
                else:
                    service_no = ""
                print("Service :", service_no)
                if service_no == '612':
                    running_app_channel = "TF1"
                if service_no == '201':
                    running_app_channel = "France 2"
                if service_no == '298':
                    running_app_channel = "France 3"
                if service_no == '1024':
                    running_app_channel = "Canal+"
                if service_no == '203':
                    running_app_channel = "France 5"
                if service_no == '613':
                    running_app_channel = "M6"
                if service_no == '204':
                    running_app_channel = "Arte"
                if service_no == '372':
                    running_app_channel = "C8"
                if service_no == '373':
                    running_app_channel = "W9"
                if service_no == '497':
                    running_app_channel = "TMC"
                if service_no == '374':
                    running_app_channel = "TFX"
                if service_no == '375':
                    running_app_channel = "NRJ12"
                if service_no == '226':
                    running_app_channel = "LCP"
                if service_no == '376':
                    running_app_channel = "France 4"
                if service_no == '400':
                    running_app_channel = "BFM TV"
                if service_no == '679':
                    running_app_channel = "CNews"
                if service_no == '678':
                    running_app_channel = "CStar"
                if service_no == '677':
                    running_app_channel = "Gulli"
                if service_no == '238':
                    running_app_channel = "France Ô"
                if service_no == '993':
                    running_app_channel = "TF1 Films & Series"
                if service_no == '994':
                    running_app_channel = "L'équipe 21"
                if service_no == '995':
                    running_app_channel = "6TER"
                if service_no == '996':
                    running_app_channel = "RMC Story"
                if service_no == '997':
                    running_app_channel = "RMC Découverte"
                if service_no == '998':
                    running_app_channel = "Chérie 25"
                if service_no == '1145':
                    running_app_channel = "LCI"
                if service_no == '1173':
                    running_app_channel = "France Info TV"
                if service_no == '213':
                    running_app_channel = "Paris Première"
                if service_no == '210':
                    running_app_channel = "RTL9"

                log = str(subprocess.check_output("adb logcat -d -t 5000 |grep -E 'MediaAttributes: ' |tail -n 1", shell=True, timeout=10))
                running_app_infos = re.search('MediaAttributes: (.+) - ', log, re.IGNORECASE)
                if (running_app_infos):
                    running_app_infos = running_app_infos.group(1)            
            else:
                running_app_channel = "None"


        else:
            running_app = 'TV Off/Asleep'

        Devices[1].Update(nValue=1, sValue=str(running_app))
        Devices[2].Update(nValue=1, sValue=str(running_app_channel))
        Devices[3].Update(nValue=1, sValue=str(running_app_infos))
        Devices[4].Update(nValue=1, sValue=str(running_package))
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
