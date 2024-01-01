import sys
import psutil
import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from clientProtocol import ClientProtocol
from threading import Thread
from time import sleep


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
    newRoom = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{prot.uName} Just Chat!")

        self.rooms = {}

        self.move(589,269)
        self.setFixedSize(740,515)
        
        self.online = QTableWidget(self)
        self.online.setGeometry(1,0,150,509)
        self.rowLimit = 1
        self.online.setRowCount(self.rowLimit)
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

        checkTab = Thread(target = self.tabCheck)
        checkTab.start()

        self.chatUpdate.connect(self.Room_update)
        self.newRoom.connect(self.createRoom)
        self.userUpdate.connect(self.tableUpdate)

    def tabCheck(self):
        sleep(1)
        cur = 0
        while True:
            newCur = self.chatTabs.currentIndex()
            if newCur != cur:
                cur = newCur
                rName = self.chatTabs.tabText(cur)
                self.userUpdate.emit(rName)
        
    def tableUpdate(self,rName):
        if self.online.rowCount() > 1:
            for i in range(1,self.online.rowCount()):
                self.online.removeRow(i)
        if self.chatTabs.tabText(self.chatTabs.currentIndex()) == rName:
            if rName == 'Server Room':
                self.rowLimit = 1
                self.online.setRowCount(self.rowLimit)
                for i in range(1,self.online.rowCount()):
                    self.online.removeRow(i)
            elif len(self.rooms[rName]) != 0:
                print(len(self.rooms[rName]),self.rooms[rName])
                self.rowLimit = len(self.rooms[rName]) + 1
                print(self.rowLimit)
                self.online.setRowCount(self.rowLimit)
                pos = 0
                for j in self.rooms[rName]:
                    pos += 1
                    self.online.setItem(pos,0,QTableWidgetItem(j))

    def tabClose(self,index):
        if index == 0:
            return
        rname = self.chatTabs.tabText(index)
        self.chatTabs.removeTab(index)
        prot.send(prot.client_socket,Name = prot.uName,msg = f"/leave {rname}",To = 'Server')

    def createRoom(self,name):
        tab = QTextEdit(self)
        tab.setReadOnly(True)
        self.chatTabs.addTab(tab,name)
        idx = self.chatTabs.count() - 1
        self.Room_update("green",f"Server :> Welcome to the room {name}",idx)
        self.rooms[name] = []


    def keyPressEvent(self, e: QKeyEvent | None):
        if (e.key() == 16777220) or (e.key() == 16777221):
            return self.sendMsg()

    def emitSignal (self,color = '',text = '',status = '',index = ''):
        if status == 0:
            self.chatUpdate.emit(color,text,index)
        elif status == 1:
            self.newRoom.emit((text.split())[1])
        else:
            self.userUpdate.emit(text)

    def Room_update(self,color = 'black',text = '',index = 0):
        self.chatTabs.widget(index).append(prot.formatResult(color,text))

    def sendMsg(self):
        if self.msg.text() != '' and prot.connected:
            if self.chatTabs.currentIndex() == 0:
                to = 'Server'
            else:
                to = self.chatTabs.tabText(self.chatTabs.currentIndex())
            prot.send(prot.client_socket,Name = prot.uName,msg = self.msg.text(),To = to)
            self.Room_update(color = 'dark violet', text = f'ME :> {self.msg.text()}',index = self.chatTabs.currentIndex())
            self.msg.clear()
        elif not prot.connected:
            self.Room_update(color = 'red', text = 'You are not connected to a server!')
        else:
            pass

    def received(self,msg):
        if msg['Name'] == 'Server':
            text = msg['msg']
            if 'created' in msg['msg'] or 'joined!' in msg['msg']:
                self.emitSignal(text = msg['msg'],status = 1)
            elif 'left' in msg['msg']:
                rname = ((msg['msg'].split('room'))[1]).strip()
                if 'You left' in msg['msg']:
                    try:                        
                        for i in range(self.chatTabs.count()):
                            if self.chatTabs.tabText(i) == rname:
                                self.chatTabs.removeTab(i)
                                break
                    except:
                        pass
                else:
                    self.rooms[rname].remove((msg['msg'].split('left'))[0].strip())
                    print((msg['msg'].split('left'))[0].strip(),'left')
                    self.userUpdate.emit(rname)
            elif "Online:" in msg['msg']:
                on = text.split('Online:')[1]
                try:
                    on = on.split()
                    for i in on:
                        self.rooms[msg['To']].append(i)
                except:
                    self.rooms[msg['To']].append(on)
                self.userUpdate.emit(msg['To'])
            self.emitSignal('brown',f"Server :> {text}",0,0)
            return
        for i in range(1,self.chatTabs.count()):
            if self.chatTabs.tabText(i) == msg['To']:
                break
        self.emitSignal('brown',f"{msg['Name']} :> {msg['msg']}",False,i)

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
