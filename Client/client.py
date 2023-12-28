import sys
import os
import socket
import errno
import threading
import psutil

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *

import clientProtocol

prot = clientProtocol.ClientProtocol()

def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()

class chatWin(QMainWindow):
    def __init__(self):
        super().__init__()

        #To Get Name

        self.setWindowTitle('Choose Name!')

        self.setFixedSize(350,150)
        #cp = QDesktopWidget().availableGeometry().center()
        #print(cp)

        self.mainFrame1 = QWidget(self)
        self.mainFrame1.setFixedSize(350,150)

        label = QLabel('Enter your User Name')
        label.setParent(self.mainFrame1)
        label.move(90,20)
        label.setStyleSheet("font-size: 10pt")
        self.name = QLineEdit(self.mainFrame1)
        self.name.setMaxLength(10)
        self.name.move(97,60)
        self.name.setStyleSheet("font-size: 10pt")

        self.start = QPushButton("Start Server")
        self.start.setParent(self.mainFrame1)
        self.start.move(125,105)
        self.start.setStyleSheet("font-size: 10pt")
        self.start.clicked.connect(self.setName)

        #The Chat Window

        self.mainFrame2 = QWidget()
        self.mainFrame2.setFixedSize(740,480)
        
        self.online = QTableWidget(self.mainFrame2)
        self.online.setGeometry(1,0,250,479)
        self.online.setRowCount(0)
        self.online.setColumnCount(1)
        self.online.setHorizontalHeaderLabels(['Online Now'])

        self.chatView = QTextEdit(self.mainFrame2)
        self.chatView.setReadOnly(True)
        self.chatView.setGeometry(255,0,489,444)

        self.msg = QLineEdit(self.mainFrame2)
        self.msg.setGeometry(255,449,390,30)
        self.btn = QPushButton('Send')
        self.btn.setParent(self.mainFrame2)
        self.btn.setGeometry(650,449,90,30)

    def chatView_update(self,color = 'black',text = ''):
        self.chatView.append(prot.formatResult(color,text))

    def keyPressEvent(self, e: QKeyEvent | None):
        if (e.key() == 16777220) or (e.key() == 16777221):
            print('Enter pressed')

    def setName(self):
        if self.name.text() != '':
            prot.uName = self.name.text()
            self.move(589,269)
            self.setFixedSize(740,480)
            self.mainFrame1.setParent(None)
            self.mainFrame2.setParent(self)
            self.setWindowTitle(f"{prot.uName} Just Chat!")
            self.setCentralWidget(self.mainFrame2)


class NamePopUp(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        
        self.exec_()

    def keyPressEvent(self, e: QKeyEvent | None):
        if (e.key() == 16777220) or (e.key() == 16777221):
            return self.setName()



if __name__ == '__main__':

    def suppress_qt_warnings():
        os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
        os.environ["QT_SCALE_FACTOR"] = "1"

    suppress_qt_warnings()

    app = QApplication(sys.argv)
    window = chatWin()
    prot.window = window
    window.show()
    app.exec_()
