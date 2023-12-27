from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys
import serverProtocol as prot

class serverWin(QMainWindow):
    def __init__(self):
        super().__init__()

        '''Server backend variables here'''
        self.socket_list = []
        self.clients = {}

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
        self.start.clicked.connect(startServer)
        self.exit = QPushButton('Exit')

        self.mainGrid.addWidget(self.clientTable,0,0,4,3,Qt.AlignmentFlag(0))
        self.mainGrid.addWidget(self.textEdit,0,3,4,4,Qt.AlignmentFlag(0))
        self.mainGrid.addWidget(self.start,4,3)
        self.mainGrid.addWidget(self.exit,4,6)

        def startServer(self):
            self.start.setEnaabled(False)


app = QApplication(sys.argv)

window = serverWin()
window.show()

app.exec()