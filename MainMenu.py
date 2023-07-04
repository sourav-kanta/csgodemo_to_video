import sys
from PyQt5 import QtWidgets

from AppWindow import Ui_MainWindow
from SetupWindow import Ui_Dialog
import recorder
import os 
from threading import Thread


class UiDialog(QtWidgets.QDialog, QtWidgets.QMainWindow):
    parent = None
    def setSteamFolder(self):
        recorder.settings['steamPath'] = os.path.abspath(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Steam Folder'))
        recorder.settings['logFile'] = os.path.join(recorder.settings['steamPath'],
                                                     "steamapps\\common\\Counter-Strike Global Offensive\\csgo\\console.log")        
        recorder.settings['cfgFolder'] = os.path.join(recorder.settings['steamPath'],
                                                     "steamapps\\common\\Counter-Strike Global Offensive\\csgo\\cfg") 
    def selectDemo(self):
        recorder.settings['demoFile'] =  os.path.abspath(QtWidgets.QFileDialog.getOpenFileName(self, 'Select demo file')[0])
        recorder.settings['vdmFile'] = os.path.dirname(recorder.settings['demoFile']) + "\\" + os.path.basename(recorder.settings['demoFile']).replace(".dem", ".vdm") 
    def setPlayerName(self) :
        recorder.settings['playerName'] = self.ui.playerName.text()
    
    def selectObs(self) :
        recorder.settings['obsFile'] = os.path.abspath(QtWidgets.QFileDialog.getOpenFileName(self, 'Select file')[0])
        
    def saveSetup(self) :
        self.setPlayerName()
        for key, value in recorder.settings.items() :
            if value == "":
                msg = QtWidgets.QMessageBox()
                msg.setText("Setup did not complete successfully. Please retry")
                msg.setWindowTitle("Error")
                msg.exec_()
                return
        recorder.saveSettings()
        self.parent.refreshLabels()
        recorder.logSettings()
        recorder.updateCfg()
        
    def __init__(self, mainWindow):
        super().__init__()
        self.parent = mainWindow
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.selectSteam.clicked.connect(self.setSteamFolder)
        self.ui.selectObs.clicked.connect(self.selectObs)
        self.ui.selectDemo.clicked.connect(self.selectDemo)
        self.ui.buttonBox.accepted.connect(self.saveSetup)

class AppWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
    shouldUpdateLabel = False

    def refreshLabels(self) :
        self.steamPath.setText(recorder.settings['steamPath'])
        self.obsPath.setText(recorder.settings['obsFile'])
        self.playerName.setText(recorder.settings['playerName'])
        self.demoPath.setText(recorder.settings['demoFile'])
    
    def changeSetup(self):
        dialog = UiDialog(self)
        dialog.exec()

    def automationThread(self) :
        recorder.pythoncom.CoInitialize()
        self.progressBar.setProperty("value", 0)
        recorder.startObs()
        self.progressBar.setProperty("value", 5)
        recorder.startCs()   
        self.progressBar.setProperty("value", 10)
        recorder.createVdmFile() 
        self.progressBar.setProperty("value", 15)
        recorder.time.sleep(50)
        recorder.playFinalDemo()
        recorder.time.sleep(50)
        recorder.startRecording()
        self.progressBar.setProperty("value", 20)
        recorder.waitTillDemoFinish()
        self.progressBar.setProperty("value", 90)
        recorder.stopRecording()
        self.progressBar.setProperty("value", 100)
        self.shouldUpdateLabel = False
        self.setupBtn.setEnabled(True)
        self.startProcess.setEnabled(True)

    def updateLabel(self) :
        while self.shouldUpdateLabel :
            with open('logfile.log', 'r') as logF:
                self.consoleOut.setText(logF.read())
            recorder.time.sleep(1)


    def startAutomation(self) :
        self.shouldUpdateLabel = True
        updateThread = Thread(target = self.updateLabel)
        autoThread = Thread(target = self.automationThread)
        updateThread.start()
        autoThread.start()
        self.setupBtn.setEnabled(False)
        self.startProcess.setEnabled(False)

    def __init__(self, *args, obj=None, **kwargs):
        super(AppWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.refreshLabels()
        self.setupBtn.clicked.connect(self.changeSetup)
        self.startProcess.clicked.connect(self.startAutomation)


app = QtWidgets.QApplication(sys.argv)
window = AppWindow()
window.show()
app.exec()