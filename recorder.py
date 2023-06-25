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

logFile = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive\\csgo\\console.log"
steamPath = "C:\\Program Files (x86)\\Steam\\"
vdmFile = "C:\\Users\\soura\\OneDrive\\Desktop\\scripts\\demo\\demo.vdm"
tickfile = "C:\\Users\\soura\\OneDrive\\Desktop\\scripts\\ticks.txt" 
playername = 'buddha#skinsmonkey'

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
        
def runCmd(cmd) :
    proc = subprocess.Popen(cmd, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if stderr :
        print("Error while executing : " + cmd + " : " + stderr)
      
def waitForText(text) :
    while True :
        if os.path.isfile(logFile) : 
            with open(logFile, 'r') as logF :
                logLines = logF.readlines()
                for line in logLines : 
                    if re.search(text, line) :
                        return 

def checkIfCsReady() : 
    waitForText('Map: awp_mirage')

def waitTillDemoReady() :
    waitForText('DemoStartedRecording')            

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

def makeCsActiveWindow() :
    w = WindowMgr()
    w.find_window_wildcard("Counter-Strike: Global Offensive")
    w.set_foreground()

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
            
def playFinalDemo() :
    print("Playing Final demo")
    makeCsActiveWindow()
    time.sleep(3)
    keypress.SimulateKey(keypress.VK_T)

def startObs() :
    return

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
    

def startRecording() :
    host = "localhost"
    port = 4455
    ws = obsws(host, port)
    ws.connect()
    try:
        ws.call(requests.StartRecord())
        makeCsActiveWindow()
        keypress.SimulateKey(keypress.VK_M)
        time.sleep(5)
        keypress.SimulateKey(keypress.VK_M)
        waitTillDemoFinish()
        ws.call(requests.StopRecord())
        runCmd("taskkill /f /im csgo.exe")
    except KeyboardInterrupt:
        pass
    ws.disconnect()   

startObs()
startCs()   
createVdmFile() 
time.sleep(50)
playFinalDemo()
time.sleep(50)
startRecording()
