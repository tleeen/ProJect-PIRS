from Assistant import *
from gui_new_concept_9 import *
from ui_functions import *
from ui_splash_screen_2 import Ui_SplashScreen
import sys

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
        self.ui.pushButton_2.clicked.connect(self.Pirs.voice_activation)
        self.ui.pushButton_2.clicked.connect(self.fix_label)
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

        ## ==> END ##

        ## PAGES
        ########################################################################

        # PAGE 1
        self.ui.btn_home.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_home))

        # PAGE 2
        self.ui.btn_user.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_user))

        # PAGE 3
        self.ui.btn_settings.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_settings))

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

        self.ui.pushButton.clicked.connect(self.getCommand)


        ## ==> LOAD DEFINITIONS
        ########################################################################
        UIFunctions.uiDefinitions(self)
        ## ==> END ##

        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##
    def fix_label(self):
        self.ui.label_6.setText("Активирован")

    # USER COMANDS
    def getCommand(self):
        url = self.ui.lineEdit.text()
        command = self.ui.lineEdit_2.text()
        if command != "" and url != "":
            self.ui.label_4.setText("")
            with open("commands.txt", "a") as file:
                file.write(url + ";" + command + "\n")
            self.ui.lineEdit.clear()
            self.ui.lineEdit_2.clear()
        else:
            self.ui.label_4.setText("Не все поля были заполнены")
    
    def closeApp(self):
        self.threadPirs.exit()
        self.threadPirs.terminate()
        self.threadPirs.wait(500)
        self.close()
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
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = SplashScreen()
    sys.exit(app.exec_())