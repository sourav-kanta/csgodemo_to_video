# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 08:26:59 2023

@author: soura
"""

import os
import subprocess
import time
import keypress
import pywintypes
import win32gui
import re
import win32com.client
from obswebsocket import obsws, requests
import shutil 
import json
import logging
import pythoncom

logging.basicConfig(filename="logfile.log",
                    format='%(message)s',
                    filemode='w')

logger = logging.getLogger("MyApp")
logger.setLevel(logging.DEBUG)

settings = { "logFile" : "",
    "steamPath" : "",
    "tickfile" : "ticks.txt",
    "demoFile" : "",
    "vdmFile" : "",
    "playerName" : '',
    "obsFile" : "",
    "cfgFolder" : ""
    }

if os.path.isfile('settings.json'):
    settingsF = open('settings.json')
    settings = json.load(settingsF)

def logSettings() :
    logger.info(json.dumps(settings, indent=4))

# OBS websocket connection
host = "localhost"
port = 4455
ws = obsws(host, port)

def saveSettings() :
    with open('settings.json', 'w') as f:
        json.dump(settings, f)

def updateCfg() :
    with open('recording.cfg', 'r') as cfgF :
        cfgContent = cfgF.read()
        cfgContent = cfgContent.replace('<DEMO_FILE>',settings['demoFile'])
        cfgContent = cfgContent.replace('<PLAYER_NAME>',settings['playerName'])
        csgoCfgFile = os.path.join(settings['cfgFolder'], "recording.cfg")
        with open(csgoCfgFile, 'w') as csCfgF :
            csCfgF.write(cfgContent)

# Class to handle window switching to CSGO
# Blatantly copied from stackoverflow !
class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(self._handle)

# Run a command on windows shell        
def runCmd(cmd) :
    proc = subprocess.Popen(cmd, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if stderr :
        logger.info("Error while executing : " + cmd + " : " + stderr)

# Wait till text is found in console.log file        
def waitForText(text) :
    while True :
        if os.path.isfile(settings['logFile']) : 
            with open(settings['logFile'], 'r', errors='ignore') as logF :
                logLines = logF.readlines()
                for line in logLines : 
                    if re.search(text, line) :
                        return 

# Check if we can use binds 
# Binds in csgo only works if we are in a map and not on main menu
def checkIfCsReady() : 
    waitForText('Map: awp_mirage')

# Wait till demo loads first time 
# Using this to run demo_listimportantticks
def waitTillDemoReady() :
    waitForText('DemoStartedRecording')            

# Start csgo
def startCs() :
    startCmd = "start /d \"" + settings['steamPath'] + "\" steam.exe  -applaunch 730 -windowed -condebug -insecure +exec recording"
    logger.info("Run CsGO : " + startCmd)
    if os.path.isfile(settings['logFile']) : 
        os.remove(settings['logFile'])
    if os.path.isfile(settings['vdmFile']) : 
        os.remove(settings['vdmFile'])
    runCmd(startCmd)
    checkIfCsReady()
    time.sleep(30)
    logger.info("CS GO ready now")

# Switch current window to CSGO. Done to avoid user minimising CS
def makeCsActiveWindow() :
    w = WindowMgr()
    w.find_window_wildcard("Counter-Strike: Global Offensive")
    w.set_foreground()

# Separate out the Tick entries from console.log file after
# running command : demo_listimportantticks
def writeTickFile() :
    time.sleep(10)
    if os.path.isfile(settings['tickfile']) :
        os.remove(settings['tickfile'])
    with open(settings['tickfile'], 'w') as tickF:
        logger.info("Writing tick file")
        if os.path.isfile(settings['logFile']) : 
            with open(settings['logFile'], 'r', errors='ignore') as logF :
                logLines = logF.readlines()
                for line in logLines : 
                    if "Tick:" in line :
                        tickF.write(line.rstrip() + "\n")

# Generate the VDM file contents. Using this to skip from player death
# to next round
def generateVdmContent() :
    vdmLines = []
    vdmLines.append('demoactions\n')
    vdmLines.append('{\n')
    action = 1
    startTick = 0
    endTick = 0
    live = 0
    with open(settings['tickfile'], 'r') as tickF:
        for line in tickF :
            if live == 0 :
                if "Event: cs_pre_restart" in line :
                    live = 1
                    endTick = int(re.search("Tick: ([0-9]*)", line).group(1))
                    vdmLines.append("\t\"" + str(action) + "\"\n")
                    vdmLines.append("\t{\n")
                    vdmLines.append("\t\tfactory \"SkipAhead\"\n")
                    vdmLines.append("\t\tname \"Unnamed" + str(action) + "\"\n")
                    vdmLines.append("\t\tstarttick \"" + str(startTick) + "\"\n")
                    vdmLines.append("\t\tskiptotick\"" + str(endTick) + "\"\n")
                    vdmLines.append("\t}\n")
                    action = action + 1
                    vdmLines.append("\t\"" + str(action) + "\"\n")
                    vdmLines.append("\t{\n")
                    vdmLines.append("\t\tfactory \"PlayCommands\"\n")
                    vdmLines.append("\t\tname \"Unnamed" + str(action) + "\"\n")
                    vdmLines.append("\t\tstarttick \"" + str(endTick+10) + "\"\n")
                    vdmLines.append("\t\tcommands\"demo_pause\"\n")
                    vdmLines.append("\t}\n")
                    action = action + 1
                continue
            if 'killed ' + settings['playerName'] in line :
                startTick = int(re.search("Tick: ([0-9]*)", line).group(1))
            if 'Event: round_start' in line :
                if startTick > endTick:
                    endTick = int(re.search("Tick: ([0-9]*)", line).group(1))
                    vdmLines.append("\t\"" + str(action) + "\"\n")
                    vdmLines.append("\t{\n")
                    vdmLines.append("\t\tfactory \"SkipAhead\"\n")
                    vdmLines.append("\t\tname \"Unnamed" + str(action) + "\"\n")
                    vdmLines.append("\t\tstarttick \"" + str(startTick) + "\"\n")
                    vdmLines.append("\t\tskiptotick\"" + str(endTick) + "\"\n")
                    vdmLines.append("\t}\n")
                    action = action + 1
    vdmLines.append('}\n')
    with open(settings['vdmFile'],'w') as vdmF :
        vdmF.writelines(vdmLines)

# Generate the vdm file
def createVdmFile() :
    logger.info("Starting Demo")
    makeCsActiveWindow()
    keypress.SimulateKey(keypress.VK_DOT)
    waitTillDemoReady()
    time.sleep(60)
    makeCsActiveWindow()
    logger.info("Dumping ticks")
    keypress.SimulateKey(keypress.VK_L)
    writeTickFile()
    generateVdmContent()
            
# Again load the demo after vdm file has been created    
def playFinalDemo() :
    logger.info("Playing Final demo")
    makeCsActiveWindow()
    time.sleep(3)
    keypress.SimulateKey(keypress.VK_T)

# Increase usability so user doest have to keep OBS running
def startObs() :
    # sample cmd start /d "C:\Program Files\obs-studio\bin\64bit" "" obs64.exe
    obsCmd = "start /d \"" + os.path.dirname(settings['obsFile']) + "\" \"\" obs64.exe"
    logger.info("OBS command : " + obsCmd)
    runCmd(obsCmd)
    time.sleep(10)
    ws.connect()
    return

# Check if the final demo has finished. Check if the searched message
# appears twice in console.log. If yes we know demo finished playing 
def waitTillDemoFinish() :
    while True :
        if os.path.isfile(settings['logFile']) : 
            with open(settings['logFile'], 'r', errors='ignore') as logF :
                logLines = logF.readlines()
                statemsg = 0
                for line in logLines : 
                    if re.search('ChangeGameUIState: CSGO_GAME_UI_STATE_INGAME -> CSGO_GAME_UI_STATE_MAINMENU', line) :
                        if statemsg == 0 :
                            statemsg = 1
                        elif statemsg == 1 :
                            logger.info("Demo Finished")
                            return 
    
# Final demo has loaded. Start recording
def startRecording() :
    try:
        # Automated OBS scene creation so user doesnt have to 
        # worry about adding CSGO as a source
        ws.call(requests.CreateScene(sceneName = "CS Demo"))
        sources = ws.call(requests.CreateInput(sceneName="CS Demo",
                                     inputName="CS Window",
                                     inputKind = "window_capture",
                                     inputSettings = {
                                         'window': 'Global Offensive:Valve001:csgo.exe'
                                         }))
        ws.call(requests.SetCurrentProgramScene(sceneName = "CS Demo"))
        scrId = sources.datain["sceneItemId"]
        transformObj = {'boundsHeight': 720.0, 'boundsType': 'OBS_BOUNDS_STRETCH', 'boundsWidth': 1280.0}
        ws.call(requests.SetSceneItemTransform(sceneName = "CS Demo", sceneItemId = scrId, sceneItemTransform = transformObj))
        ws.call(requests.StartRecord())
        makeCsActiveWindow()
        # Awkward hack as CSGO does seem to spectate player in warmup
        # To fix pressing the bind m twice to make sure 
        keypress.SimulateKey(keypress.VK_M)
        time.sleep(5)
        keypress.SimulateKey(keypress.VK_M)
    except KeyboardInterrupt:
        stopRecording()
       
# Demo playback finished. Stop recording, kill csgo, copy output file to 
# <folder you downloaded repository>\\demo folder, disconnect OBS websocket
def stopRecording() :
    recResponse = ws.call(requests.StopRecord())
    ws.call(requests.RemoveScene(sceneName = "CS Demo"))
    runCmd("taskkill /f /im csgo.exe")
    ws.disconnect()
    runCmd("taskkill /f /im obs64.exe")
    videoFile = recResponse.datain['outputPath']
    dirPath = os.path.dirname(settings['vdmFile'])
    dstVideoFile = os.path.join(dirPath,'demo.mkv')
    shutil.copy(videoFile,dstVideoFile)
    os.remove(videoFile)

# Driver 
# TODO drive through buttons on GUI
# Thinking of adding PyQt interface for seeting up global variables and buttons
# for recording demo videos and uploading to youtube
#startObs()
#startCs()   
#createVdmFile() 
#time.sleep(50)
#playFinalDemo()
#time.sleep(50)
#startRecording()
#waitTillDemoFinish()
#stopRecording()
