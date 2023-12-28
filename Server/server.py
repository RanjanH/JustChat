from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from threading import *
from Crypto.PublicKey import RSA

import sys
import serverProtocol
import socket
import os
import psutil

prot = serverProtocol.ServerProtocol()

def killProcess(pid, includeParent = True):
    parent = psutil.Process(pid)
    if includeParent:
        parent.kill()

class serverWin(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Just Chat Server!")
        self.setFixedSize(QSize(800,450))

        self.mainFrame = QWidget(self)
        self.mainFrame.setGeometry(0,0,800,450)
        self.mainGrid = QGridLayout()
        self.mainFrame.setLayout(self.mainGrid)

        self.clientTable = QTableWidget()
        self.clientTable.setColumnCount(3)
        self.table_row = 0
        self.clientTable.setRowCount(self.table_row)
        self.clientTable.setHorizontalHeaderLabels(['Name','Host','Port'])
        
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)

        self.start = QPushButton('Start Server')
        self.start.clicked.connect(prot.startServer)
        self.exit = QPushButton('Exit')

        self.mainGrid.addWidget(self.clientTable,0,0,4,3,Qt.AlignmentFlag(0))
        self.mainGrid.addWidget(self.textEdit,0,3,4,4,Qt.AlignmentFlag(0))
        self.mainGrid.addWidget(self.start,4,3)
        self.mainGrid.addWidget(self.exit,4,6)

    def textEdit_update(self,color = 'black',text = ''):
        self.textEdit.append(prot.formatResult(color,text))

    def updateTable(self,update,*args):
        if update == True:
            curRow = self.clientTable.rowCount()
            self.clientTable.insertRow(curRow)
            for i in range(3):
                self.clientTable.setItem(curRow,i,QTableWidgetItem(str(args[i])))

        else:
            found = False
            for row in range(self.clientTable.rowCount()):
                name = self.clientTable.item(row,0).text()
                add = self.clientTable.item(row,1).text()
                port = self.clientTable.item(row,2).text()
                if (name,add,int(port)) == args:
                    found = True
                    break
            if found:
                self.clientTable.removeRow(row)


if __name__ == "__main__":

    def suppress_qt_warnings():
        os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
        os.environ["QT_SCALE_FACTOR"] = "1"

    suppress_qt_warnings()

    app = QApplication(sys.argv)
    window = serverWin()
    prot.window = window
    window.show()
    app.exec()
    me = os.getpid()
    sys.exit(killProcess(me))