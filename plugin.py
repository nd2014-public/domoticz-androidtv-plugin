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
            Domoticz.Device(Name="Running App",  Unit=1, TypeName="Text", Options=Options).Create()
            Domoticz.Device(Name="Running App Infos",  Unit=2, TypeName="Text", Options=Options).Create()

            logDebugMessage("Devices created.")

        return True

    def onCommand(self, Unit, Command, Level, Color):        
        return True

    def onHeartbeat(self):


        # Get wake or asleep :
        wake_state = 'asleep' 
        running_app = 'TV Off/Asleep'
        result = str(subprocess.check_output("adb shell dumpsys power |grep 'mWakefulness'", shell=True, timeout=10))
        if (result.find('mWakefulness=Awake') > -1):
            wake_state='awake'
            running_app = 'Other app'
        

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
                log = str(subprocess.check_output("adb logcat -d -t 5000 |grep -E 'vodservice' | tail -n 1", shell=True, timeout=10))
                vod_search = re.search('android.intent.action.VIEW dat=vodservice://(.*) flg=', log, re.IGNORECASE)
                if vod_search:
                    print("VOD found ...", vod_search)
                    running_app_infos = vod_search.group(1)
            elif (running_app == "TV"):
                log = str(subprocess.check_output("adb logcat -d -t 5000 |grep -E 'open rtsp://rtsp-server/fbxtv_priv/stream' | tail -n 1", shell=True, timeout=10))
                service_no = re.search('service=([0-9]+)', log, re.IGNORECASE)
                print "Service :", service_no
                if service_no == '612':
                    running_app_infos = "TF1"
                if service_no == '201':
                    running_app_infos = "France 2"
                if service_no == '298':
                    running_app_infos = "France 3"
                if service_no == '1024':
                    running_app_infos = "Canal+"
                if service_no == '203':
                    running_app_infos = "France 5"
                if service_no == '613':
                    running_app_infos = "M6"
                if service_no == '204':
                    running_app_infos = "Arte"
                if service_no == '372':
                    running_app_infos = "C8"
                if service_no == '373':
                    running_app_infos = "W9"
                if service_no == '497':
                    running_app_infos = "TMC"
                if service_no == '374':
                    running_app_infos = "TFX"
                if service_no == '375':
                    running_app_infos = "NRJ12"
                if service_no == '226':
                    running_app_infos = "LCP"
                if service_no == '376':
                    running_app_infos = "France 4"
                if service_no == '400':
                    running_app_infos = "BFM TV"
                if service_no == '679':
                    running_app_infos = "CNews"
                if service_no == '678':
                    running_app_infos = "CStar"
                if service_no == '677':
                    running_app_infos = "Gulli"
                if service_no == '238':
                    running_app_infos = "France Ô"
                if service_no == '993':
                    running_app_infos = "TF1 Films & Series"
                if service_no == '994':
                    running_app_infos = "L'équipe 21"
                if service_no == '995':
                    running_app_infos = "6TER"
                if service_no == '996':
                    running_app_infos = "RMC Story"
                if service_no == '997':
                    running_app_infos = "RMC Découverte"
                if service_no == '998':
                    running_app_infos = "Chérie 25"
                if service_no == '1145':
                    running_app_infos = "LCI"
                if service_no == '1173':
                    running_app_infos = "France Info TV"
                if service_no == '213':
                    running_app_infos = "Paris Première"
                if service_no == '210':
                    running_app_infos = "RTL9"
            else:
                running_app_infos = "None"


        else:
            running_app = 'TV Off/Asleep'

        Devices[1].Update(nValue=1, sValue=str(running_app))
        Devices[2].Update(nValue=1, sValue=str(running_app_infos))
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
