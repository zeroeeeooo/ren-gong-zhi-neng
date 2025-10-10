from PySide2.QtWidgets import QApplication,QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile 


class startpage:
    def __init__(self):
        self.ui = QUiLoader().load("./src/ui/主界面.ui")
        self.ui.startbtn.clicked.connect(self.startbtn_click)
        self.ui.exitbtn.clicked.connect(self.exitbtn_click)
        self.ui.setWindowTitle("五子棋")
    def startbtn_click(self):
        QMessageBox.information(self.ui, "提示", "开始游戏")
    def exitbtn_click(self):
        self.ui.close()

app = QApplication([])
stats = startpage()
stats.ui.show()
app.exec_()