import sys
from PyQt5 import QtGui, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QAction, qApp, QMenu, QGraphicsDropShadowEffect, \
    QMainWindow
from pycaw.pycaw import AudioUtilities
from ui_splash_screen import Ui_SplashScreen
from Assistant import *

## ==> GLOBALS
counter = 0

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # download and show main window
        self.ui = uic.loadUi(r"gui\gui_pirs.ui")
        self.ui.setWindowFlag(Qt.FramelessWindowHint)
        self.ui.show()
        self.ui.start.setGraphicsEffect(self.shadow())

        # control buttons on main window
        self.ui.Exit.clicked.connect(self.close_win)
        self.ui.Roll_up.clicked.connect(self.ui.showMinimized)

        # Pirs's functions
        self.thread = QtCore.QThread()
        self.Pirs = Assistant()
        self.Pirs.moveToThread(self.thread)
        self.ui.start.clicked.connect(self.Pirs.voice_activation)
        self.ui.start.clicked.connect(self.fix_label)
        self.thread.start()

        # tray menu
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(r"gui\icons\tray_logo.ico"))

        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.ui.show)
        hide_action.triggered.connect(self.ui.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # download and show settings
        self.settings = uic.loadUi(r"gui\settings.ui")
        self.settings.setWindowIcon(QtGui.QIcon(r"gui\icons\Settings.ico"))
        self.settings.setWindowFlag(Qt.FramelessWindowHint)
        self.ui.settingsButton.clicked.connect(self.show_settings)
        self.settings.ok.clicked.connect(self.getCommand)

        # control buttons on settings window
        self.settings.Exit.clicked.connect(self.settings.close)
        self.settings.Roll_up.clicked.connect(self.settings.showMinimized)

        # speakers
        self.settings.speaker.setMinimum(0)
        self.settings.speaker.setMaximum(100)
        self.settings.speaker.setSingleStep(1)
        self.settings.speaker.setValue(100)
        self.settings.speaker.valueChanged.connect(self.value_speaker)
        self.settings.progressBar_2.setValue(100)
        self.settings.speaker.valueChanged[int].connect(self.func)

        # mouse click handing
        def mouseClick(event):
            if event.buttons() == Qt.LeftButton:
                self.oldPos = event.globalPos()
                self.start = event.pos()

        # move main window
        def moveWindow(event):
            if event.buttons() == Qt.LeftButton:
                self.delta = event.globalPos() - self.ui.pos() - QtCore.QPoint(65, 0)
                self.ui.move(self.ui.pos() + self.delta - self.start)

        self.ui.titleBtn.mousePressEvent = mouseClick
        self.ui.titleBtn.mouseMoveEvent = moveWindow

        # move settings window
        def moveSettings(event):
            if event.buttons() == Qt.LeftButton:
                self.delta = event.globalPos() - self.settings.pos() - QtCore.QPoint(75, 0)
                self.settings.move(self.settings.pos() + self.delta - self.start)

        self.settings.titleBtn.mousePressEvent = mouseClick
        self.settings.titleBtn.mouseMoveEvent = moveSettings

    def value_speaker(self):
        self.settings.progressBar_2.setValue(self.settings.speaker.value())

    def value_mic(self):
        self.settings.progressBar.setValue(self.settings.micro.value())

    @staticmethod
    def func(value):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session.SimpleAudioVolume
            if session.Process and session.Process.name() == "python.exe":
                volume.SetMasterVolume(value * 0.01, None)

    def show_settings(self):
        self.settings.show()

    def close_win(self):
        qApp.quit()

    # glow for objects
    @staticmethod
    def shadow():
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(0)
        shadow.setBlurRadius(110)
        shadow.setColor(QtGui.QColor(36, 172, 194))
        return shadow

    def fix_label(self):
        self.ui.label_2.setText("Pirs на связи")
        self.ui.label_2.setAlignment(Qt.AlignCenter)
        self.ui.label_2.setFont(QtGui.QFont("MS Shell Dlg 2", 24))
        self.ui.frame.setStyleSheet("background-color: rgb(152, 251, 152)")

    def getCommand(self):
        url = self.settings.url.toPlainText()
        command = self.settings.command.toPlainText()
        if command != "" or command != "":
            self.settings.warning.setText("")
            with open("commands.txt", "a") as file:
                file.write(url + ";" + command + "\n")
            self.settings.url.clear()
            self.settings.command.clear()
        else:
            self.settings.warning.setText("Не все поля были заполнены")


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
        self.timer.start(35)

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

            #SHOW MAIN WINDOW
            self.main = MainWindow()

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        counter += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SplashScreen()
    sys.exit(app.exec_())