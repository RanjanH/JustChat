import sys
import psutil
import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from clientProtocol import ClientProtocol
from threading import Thread


prot = ClientProtocol()

def killProcess(pid, including_parent=True):
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()

class nameWin(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Choose Name")

        #cp = QDesktopWidget().availableGeometry().center()
        #print(cp)

        self.setFixedSize(350,150)

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

    def setName(self):
        if self.name.text() != '':
            prot.uName = self.name.text()
        self.close()

    def keyPressEvent(self, e: QKeyEvent | None):
        if (e.key() == 16777220) or (e.key() == 16777221):
            return self.setName()

class chatWin(QMainWindow):

    chatUpdate = pyqtSignal(str,str)
    userUpdate = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{prot.uName} Just Chat!")

        self.move(589,269)
        self.setFixedSize(740,515)
        
        self.online = QTableWidget(self)
        self.online.setGeometry(1,0,250,514)
        self.online.setRowCount(0)
        self.online.setColumnCount(1)
        self.online.setHorizontalHeaderLabels(['Online Now'])

        self.chatTabs = QTabWidget(self)
        self.chatTabs.move(255,0)
        self.chatTabs.setGeometry(255,0,489,474)
        self.chatTabs.setTabsClosable(True)
        self.chatTabs.tabCloseRequested.connect(self.tabClose)

        self.commonRoom = QTextEdit(self)
        self.commonRoom.setReadOnly(True)

        self.chatTabs.addTab(self.commonRoom,'World Room')
        for i in range(10):
            self.chatTabs.addTab(QWidget(),f'Tab{i}')

        self.msg = QLineEdit(self)
        self.msg.setGeometry(255,484,390,30)
        self.btn = QPushButton('Send')
        self.btn.setParent(self)
        self.btn.setGeometry(650,484,90,30)
        self.btn.clicked.connect(self.sendMsg)

        listen = Thread(target = prot.connect)
        listen.start()

        self.chatUpdate.connect(self.commonRoom_update)

    def tabClose(self,index):
        if index == 0:
            return
        self.chatTabs.removeTab(index)

    def keyPressEvent(self, e: QKeyEvent | None):
        if (e.key() == 16777220) or (e.key() == 16777221):
            return self.sendMsg()

    def emitSignal (self,color,text,newOnline):
        if newOnline:
            self.userUpdate.emit(text)
        else:
            self.chatUpdate.emit(color,text)

    def commonRoom_update(self,color = 'black',text = ''):
        self.commonRoom.append(prot.formatResult(color,text))

    def sendMsg(self):
        if self.msg.text() != '' and prot.connected:
            prot.send(prot.client_socket,Name = prot.uName,msg = self.msg.text())
            self.commonRoom_update(color = 'dark violet', text = f'ME :> {self.msg.text()}')
            self.msg.clear()
        elif not prot.connected:
            self.commonRoom_update(color = 'red', text = 'You are not connected to a server!')
        else:
            pass

    def received(self,msg):
        self.emitSignal('brown',msg,False)

if __name__ == '__main__':

    def suppress_qt_warnings():
        os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
        os.environ["QT_SCALE_FACTOR"] = "1"

    suppress_qt_warnings()

    app = QApplication(sys.argv)
    window = nameWin()
    window.show()
    app.exec()
    window = chatWin()
    prot.window = window
    window.show()
    app.exec()
    me = os.getpid()
    sys.exit(killProcess(me))
