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
        self.name.move(87,60)
        self.name.setStyleSheet("font-size: 10pt")

        self.start = QPushButton("Start")
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

    chatUpdate = pyqtSignal(str,str,int)
    userUpdate = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{prot.uName} Just Chat!")

        self.move(589,269)
        self.setFixedSize(740,515)
        
        self.online = QTableWidget(self)
        self.online.setGeometry(1,0,150,509)
        self.online.setRowCount(1)
        self.online.setColumnCount(1)
        self.online.setHorizontalHeaderLabels(['Online Now'])
        self.online.setItem(0,0,QTableWidgetItem(f"{prot.uName} (You)"))

        self.chatTabs = QTabWidget(self)
        self.chatTabs.setGeometry(155,0,589,474)
        self.chatTabs.setTabsClosable(True)
        self.chatTabs.tabCloseRequested.connect(self.tabClose)

        self.serverRoom = QTextEdit(self)
        self.serverRoom.setReadOnly(True)

        self.chatTabs.addTab(self.serverRoom,'Server Room')

        self.msg = QLineEdit(self)
        self.msg.setGeometry(155,479,490,30)
        self.btn = QPushButton('Send')
        self.btn.setParent(self)
        self.btn.setGeometry(650,479,90,30)
        self.btn.clicked.connect(self.sendMsg)

        listen = Thread(target = prot.connect)
        listen.start()

        self.chatUpdate.connect(self.Room_update)

    def tabClose(self,index):
        if index == 0:
            return
        self.chatTabs.removeTab(index)

    def keyPressEvent(self, e: QKeyEvent | None):
        if (e.key() == 16777220) or (e.key() == 16777221):
            return self.sendMsg()

    def emitSignal (self,color,text,newOnline,index):
        if newOnline:
            self.userUpdate.emit(text)
        else:
            self.chatUpdate.emit(color,text,index)

    def Room_update(self,color = 'black',text = '',index = 0):
        self.chatTabs.widget(index).append(prot.formatResult(color,text))

    def sendMsg(self):
        if self.msg.text() != '' and prot.connected:
            if self.chatTabs.currentIndex == 0:
                to = 'Server'
            prot.send(prot.client_socket,Name = prot.uName,msg = self.msg.text(),To = to)
            self.Room_update(color = 'dark violet', text = f'ME :> {self.msg.text()}',index = self.chatTabs.currentIndex())
            self.msg.clear()
        elif not prot.connected:
            self.Room_update(color = 'red', text = 'You are not connected to a server!')
        else:
            pass

    def received(self,msg):
        if msg['Name'] == 'Server':
            self.emitSignal('brown',f"Server :> {msg['msg']}",False,0)
            return
        for i in range(1,self.chatTabs.count()):
            if self.chatTabs.tabText(i) == msg['Room']:
                break
        self.emitSignal('brown',msg,False,i)

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
