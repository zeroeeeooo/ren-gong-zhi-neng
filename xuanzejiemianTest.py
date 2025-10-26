from PySide2.QtWidgets import QApplication,QMessageBox, QLabel, QGraphicsOpacityEffect
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile 
from PySide2 import QtCore
from PySide2.QtCore import QObject, QEvent
from PySide2.QtGui import QMouseEvent, QPixmap


class XuanZeJieMian(QObject):
    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load("./src/ui/选择界面.ui")
        self.ui.setWindowTitle("五子棋 - 选择界面")
        self.ui.simplebtn.clicked.connect(self.simple_clicked)
        self.ui.minmaxbtn.clicked.connect(self.minmax_clicked)
        self.ui.randombtn.clicked.connect(self.random_clicked)
        self.selected_bot = None

    def getBotType(self):
        return self.selected_bot

    def simple_clicked(self):
        self.selected_bot = "simple_bot"
        QMessageBox.information(self.ui, "选择确认", "您选择了简单算法（Simple Bot）")
        self.ui.close()

    def minmax_clicked(self):
        self.selected_bot = "minmax_bot"
        QMessageBox.information(self.ui, "选择确认", "您选择了极小化算法（Minmax Bot）")
        self.ui.close()

    def random_clicked(self):
        self.selected_bot = "random_bot"
        QMessageBox.information(self.ui, "选择确认", "您选择了随机算法（Random Bot）")
        self.ui.close()