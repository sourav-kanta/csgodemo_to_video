# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 08:26:59 2023

@author: soura
"""

import os
import subprocess
import time
import keypress
import win32gui
import re
import win32com.client
from obswebsocket import obsws, requests
import shutil 

# Change this to "<your csgo folder>\\console.log"  
# This file is created once -condebug is added in csgo launch options
logFile = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive\\csgo\\console.log"
# Change this to your Steam directory where steam.exe is located
steamPath = "C:\\Program Files (x86)\\Steam\\"
# Change this to <folder where you pulled the repository>\\demo\\demo.vdm
# File demo.vdm will be created by this program to skip after player deaths
vdmFile = "C:\\Users\\soura\\OneDrive\\Desktop\\scripts\\demo\\demo.vdm"
# Change this to <folder where you pulled the repository>\\ticks.txt
# This file would be created to list important ticks in the demo
tickfile = "C:\\Users\\soura\\OneDrive\\Desktop\\scripts\\ticks.txt"
# Change this to your csgo username
# Has to be the username you played in the demo with 
playername = 'buddha#skinsmonkey'

# OBS websocket connection
host = "localhost"
port = 4455
ws = obsws(host, port)
ws.connect()

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
        print("Error while executing : " + cmd + " : " + stderr)

# Wait till text is found in console.log file        
def waitForText(text) :
    while True :
        if os.path.isfile(logFile) : 
            with open(logFile, 'r') as logF :
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
    os.chdir(steamPath)
    if os.path.isfile(logFile) : 
        os.remove(logFile)
    if os.path.isfile(vdmFile) : 
        os.remove(vdmFile)
    runCmd('.\\steam.exe -applaunch 730 -windowed')
    checkIfCsReady()
    time.sleep(30)
    print("CS GO ready now")

# Switch current window to CSGO. Done to avoid user minimising CS
def makeCsActiveWindow() :
    w = WindowMgr()
    w.find_window_wildcard("Counter-Strike: Global Offensive")
    w.set_foreground()

# Separate out the Tick entries from console.log file after
# running command : demo_listimportantticks
def writeTickFile() :
    time.sleep(10)
    if os.path.isfile(tickfile) :
        os.remove(tickfile)
    with open(tickfile, 'w') as tickF:
        print("Writing tick file")
        if os.path.isfile(logFile) : 
            with open(logFile, 'r') as logF :
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
    with open(tickfile, 'r') as tickF:
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
            if 'killed ' + playername in line :
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
    with open(vdmFile,'w') as vdmF :
        vdmF.writelines(vdmLines)

# Generate the vdm file
def createVdmFile() :
    print("Starting Demo")
    makeCsActiveWindow()
    keypress.SimulateKey(keypress.VK_DOT)
    waitTillDemoReady()
    time.sleep(60)
    makeCsActiveWindow()
    print("Dumping ticks")
    keypress.SimulateKey(keypress.VK_L)
    writeTickFile()
    generateVdmContent()
            
# Again load the demo after vdm file has been created    
def playFinalDemo() :
    print("Playing Final demo")
    makeCsActiveWindow()
    time.sleep(3)
    keypress.SimulateKey(keypress.VK_T)

# Increase usability so user doest have to keep OBS running
def startObs() :
    # To-Do 
    # Add a GUI to setup 
    return

# Check if the final demo has finished. Check if the searched message
# appears twice in console.log. If yes we know demo finished playing 
def waitTillDemoFinish() :
    while True :
        if os.path.isfile(logFile) : 
            with open(logFile, 'r') as logF :
                logLines = logF.readlines()
                statemsg = 0
                for line in logLines : 
                    if re.search('ChangeGameUIState: CSGO_GAME_UI_STATE_INGAME -> CSGO_GAME_UI_STATE_MAINMENU', line) :
                        if statemsg == 0 :
                            statemsg = 1
                        elif statemsg == 1 :
                            print("Demo Finished")
                            return 
    
# Final demo has loaded. Start recording
def startRecording() :
    try:
        # Automated OBS scene creation so user doesnt have to 
        # worry about adding CSGO as a source
        ws.call(requests.CreateScene(sceneName = "CS Demo"))
        ws.call(requests.CreateInput(sceneName="CS Demo",
                                     inputName="CS Window",
                                     inputKind = "window_capture",
                                     inputSettings = {
                                         'window': 'Global Offensive:Valve001:csgo.exe'
                                         }))
        ws.call(requests.SetCurrentProgramScene(sceneName = "CS Demo"))
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
    videoFile = recResponse.datain['outputPath']
    dirPath = os.path.dirname(vdmFile)
    dstVideoFile = os.path.join(dirPath,'demo.mkv')
    shutil.copy(videoFile,dstVideoFile)
    os.remove(videoFile)

# Driver 
# TODO drive through buttons on GUI
# Thinking of adding PyQt interface for seeting up global variables and buttons
# for recording demo videos and uploading to youtube
startObs()
startCs()   
createVdmFile() 
time.sleep(50)
playFinalDemo()
time.sleep(50)
startRecording()
waitTillDemoFinish()
stopRecording()
