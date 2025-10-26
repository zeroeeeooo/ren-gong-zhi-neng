from PySide2.QtWidgets import QApplication,QMessageBox,QLabel
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile 
from PySide2.QtGui import QPixmap

QiZilength = 33
QiZiheight = 33
QiZilengthGap = 50
QiZiheightGap = 63
xstartplace = 100
ystartplace = 20

class QiZi:
    def __init__(self):
        self.label = QLabel()
        self.label.setFixedSize(QiZilength, QiZiheight)

class BaiQiZi(QiZi):
    def __init__(self):
        super().__init__()
        pixmap = QPixmap("./src/picture/白子.jpg")
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
    def setPosition(self, x, y):
        self.label.move(x * QiZilengthGap+xstartplace, y * QiZiheightGap+ystartplace)

class HeiQiZi(QiZi):
    def __init__(self):
        super().__init__()
        pixmap = QPixmap("./src/picture/黑子.jpg")
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
    def setPosition(self, x, y):
        self.label.move(x * QiZilengthGap+xstartplace, y * QiZiheightGap+ystartplace)
