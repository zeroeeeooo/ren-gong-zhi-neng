from PySide2.QtWidgets import QApplication,QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile 
from duizhanTest import DuiZhanJieMian

class ZhuJieMian:
    def __init__(self):
        self.ui = QUiLoader().load("./src/ui/主界面.ui")
        self.ui.exitbtn.clicked.connect(self.exitbtn_click)
        self.ui.startbtn.clicked.connect(self.startbtn_click)
        self.ui.setWindowTitle("五子棋")
    def exitbtn_click(self):
        self.ui.close()

    def startbtn_click(self):
        self.ui.close()
        self.duizhanjiemian = DuiZhanJieMian()
        self.duizhanjiemian.ui.show()

