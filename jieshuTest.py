from PySide2.QtWidgets import QApplication,QMessageBox, QLabel, QGraphicsOpacityEffect
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile 
from PySide2 import QtCore
from PySide2.QtCore import QObject, QEvent
from PySide2.QtGui import QMouseEvent, QPixmap

class JieShuJieMian(QObject):
    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load("./src/ui/结束界面.ui")
        self.ui.setWindowTitle("结束界面")
        self.ui.continuebtn.clicked.connect(self.continue_clicked)
        self.ui.endbtn.clicked.connect(self.end_clicked)
        self.endflag = 0

    def getEndFlag(self):
        return self.endflag

    def continue_clicked(self):
        self.endflag = 0
        self.ui.close()
    def end_clicked(self):
        self.endflag = 1
        self.ui.close()