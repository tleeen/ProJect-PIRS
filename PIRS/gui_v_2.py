from Assistant import Assistant
from playsound import playsound
from gui_new_concept_13 import *
from main.ui_functions import *
from main.splash_screen import Ui_SplashScreen
from pycaw.pycaw import AudioUtilities
import sys
from main import files_rc

## ==> GLOBALS
counter = 0

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Pirs's functions
        self.threadPirs = QtCore.QThread()
        self.Pirs = Assistant()
        self.Pirs.moveToThread(self.threadPirs)
        self.ui.start_btn.clicked.connect(self.Pirs.voice_activation)
        self.ui.start_btn.clicked.connect(self.modePirs)
        self.threadPirs.start()

        ## REMOVE ==> STANDARD TITLE BAR
        UIFunctions.removeTitleBar(True)
        ## ==> END ##

        ## REMOVE ==> STANDARD TITLE BAR
        startSize = QSize(1000, 720)
        self.resize(startSize)
        self.setMinimumSize(startSize)
        # UIFunctions.enableMaximumSize(self, 500, 720)
        ## ==> END ##

        # TRAY MENU
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(r"gui\icons\tray_logo.ico"))

        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.closeApp)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        ## TOGGLE/BURGUER MENU
        ########################################################################
        self.ui.btn_toggle_menu.clicked.connect(lambda: UIFunctions.toggleMenu(self, 250, True))

        ## ==> START PAGE
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)

        ## PAGES
        ########################################################################

        # PAGE 1
        self.ui.btn_home.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_home))

        # PAGE 2
        self.ui.btn_user.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_user))

        # PAGE 3
        self.ui.btn_settings.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_settings))

        # PAGE 4
        self.ui.listCommands.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_phrases))
        self.ui.listCommands.clicked.connect(self.feedLabel)

        # MOUSE CLICK HANDING
        def mouseClick(event):
            if event.buttons() == Qt.LeftButton:
                self.start = event.pos()

        # MOVE MAIN WINDOW
        def moveWindow(event):
            if event.buttons() == Qt.LeftButton:
                self.delta = event.globalPos() - self.pos() - QtCore.QPoint(80, 10)
                self.move(self.pos() + self.delta - self.start)

        self.ui.frame_label_top_btns.mousePressEvent = mouseClick
        self.ui.frame_label_top_btns.mouseMoveEvent = moveWindow

        # GET COMMANDS
        self.ui.ok_btn.clicked.connect(self.getCommandSite)
        self.ui.ok_btn2.clicked.connect(self.getCommandFolder)
        self.ui.ok_btn3.clicked.connect(self.getNewName)

        # CHANGE VOLUME
        self.ui.horizontalSlider.setMaximum(100)
        self.ui.horizontalSlider.setValue(100)
        self.ui.progressBar.setValue(100)
        self.ui.horizontalSlider.valueChanged.connect(self.valueSpeaker)
        self.ui.horizontalSlider.valueChanged[int].connect(self.changeVolume)

        # MANUAL
        self.ui.manual_btn.clicked.connect(self.manualStart)

        ## ==> LOAD DEFINITIONS
        ########################################################################
        UIFunctions.uiDefinitions(self)
        ## ==> END ##

        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##   

    # USER COMANDS
    def getCommandSite(self):
        url = self.ui.lineEdit.text()
        command = self.ui.lineEdit_2.text()
        if command != "" and url != "":
            self.ui.warning_1.setText("")
            url.lower()
            command.lower()
            with open("commands.txt", "a") as file:
                file.write(url + ";" + command + "\n")
            self.ui.lineEdit.clear()
            self.ui.lineEdit_2.clear()
        else:
            self.ui.warning_1.setText("Не все поля были заполнены")

    def getCommandFolder(self):
        url = self.ui.lineEdit_3.text()
        command = self.ui.lineEdit_4.text()
        if command != "" and url != "":
            self.ui.warning_2.setText("")
            url.lower()
            command.lower()
            with open("commands.txt", "a") as file:
                file.write(url + ";" + command + "\n")
            self.ui.lineEdit_3.clear()
            self.ui.lineEdit_4.clear()
        else:
            self.ui.warning_2.setText("Не все поля были заполнены")
    
    def getNewName(self):
        newName = self.ui.editName.text()
        if newName != "":
            newName.lower()
            self.ui.editName.clear()
            self.Pirs.changeName(newName)
    
    def manualStart(self):
        playsound("audio/manual.mp3")

    def changeVolume(self, value):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session.SimpleAudioVolume
            if session.Process and session.Process.name() == "python.exe":
                volume.SetMasterVolume(value * 0.01, None)
    
    def valueSpeaker(self):
        self.ui.progressBar.setValue(self.ui.horizontalSlider.value())
    
    def feedLabel(self):
        self.Pirs.feedDict(self.Pirs.tasks)
        i = 1
        text = ""
        for key, value in self.Pirs.tasks.items():
            text += str(i) + ". "
            for k in key:
                text += k + ", "
            text = text[:-2]
            if isinstance(value, str):
                text += ": " + value
            text += "\n"
            i+=1
        self.ui.label_4.setText(text)

    
    def modePirs(self):
        if self.Pirs.rc.flag:
            self.Pirs.rc.flag = False
            playsound("audio/dezactivation.mp3", block=False)
            self.ui.label_6.setText("Дезактивирован")
            self.ui.label_6.setStyleSheet("color: rgb(98, 114, 164);")
        else:
            self.Pirs.rc.flag = True
            playsound("audio/activation.mp3", block=False)
            self.ui.label_6.setText("Активирован")
            self.ui.label_6.setStyleSheet("color: qlineargradient(spread:pad, x1:0, y1:0.511364, x2:1, y2:0.523, stop:0 rgba(254, 121, 199, 255), stop:1 rgba(170, 85, 255, 255));")
    
    def closeApp(self):
        self.threadPirs.exit()
        self.threadPirs.terminate()
        self.threadPirs.wait(250)
        self.close()
        self.tray_icon.hide()
        self.Pirs.bye()

# SPLASH SCREEN
class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        ## UI ==> INTERFACE CODES
        ########################################################################

        ## REMOVE TITLE BAR
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)


        ## DROP SHADOW EFFECT
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        ## QTIMER ==> START
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(25)

        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##

    ## ==> APP FUNCTIONS
    ########################################################################
    def progress(self):

        global counter

        # SET VALUE TO PROGRESS BAR
        self.ui.progressBar.setValue(counter)

        # CLOSE SPLASH SCREE AND OPEN APP
        if counter > 100:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.main = MainWindow()
            self.main.show()

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        counter += 1


if __name__ == "__main__":
    Assistant.greeting()
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = SplashScreen()
    sys.exit(app.exec_())