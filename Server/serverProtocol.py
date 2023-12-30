import socket
import select
import sys
import pickle
import struct
import dotenv
import os

from time import strftime,localtime,sleep
from Crypto.PublicKey import RSA
from threading import *

dotenv.load_dotenv()

marshall = pickle.dumps
unmarshall = pickle.loads

class ServerProtocol:
    def __init__(self):
        self.IP = os.getenv("IP")
        self.PORT = int(os.getenv("PORT"))
        self.server = ''
        self.clients = 0
        self.STATE = True
        self.socket_list = []
        self.clientMap = {}
        self.outputs = []
        self.server_key = ''
        self.server_pubKey = ''
        self.window = ''

    def timed(self):
        return strftime("%H:%M:%S",localtime())

    def formatResult(self,color = 'black',text = ''):
        return f"<font color = '{color}'>[{self.timed()}] * {text}</font>"
    
    def getName(self,client):
        return self.clientMap[client]['Name']
    
    def getAdd(self,client):
        return self.clientMap[client]['Address']

    def send(self,channel,**msg):
        buffer = marshall(msg)
        value = socket.htonl(len(buffer))
        size = struct.pack("L",value)
        channel.send(size + buffer)

    def recv(self,sock):
        size = struct.calcsize("L")
        try:
            size = sock.recv(size)
            size = socket.ntohl(struct.unpack("L",size)[0])
        except struct.error as e:
            return ''
        except :
            return False
        
        buffer = ''
        while len(buffer) < size:
            buffer = sock.recv(size - len(buffer))
        buffer = unmarshall(buffer)
        return buffer
    
    def startServer(self):
        self.window.start.setEnabled(False)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.IP,self.PORT))

        self.window.textEdit_update(color = "blue", text = "Generating RSA keys.....")

        self.server_key = RSA.generate(2048,os.urandom)
        self.server_pubKey = self.server_key.public_key()

        self.window.textEdit_update(color = "green",text = "Server is started")

        self.server.listen()
        self.socket_list.append(self.server)
        self.window.textEdit_update(color = "green",text = "Listening for clients.....")

        self.thread_event = Event()
        self.connThread = Thread(target = self.handleSocket,args = [self.thread_event])
        self.connThread.start()


    def handleSocket(self,thread_event):
        while self.STATE and not thread_event.is_set():

            ready_input,ready_output,error = select.select(self.socket_list,self.outputs,self.socket_list,3)

            for sock in ready_input:
                if sock == self.server:
                    client,address = self.server.accept()
                    cName = (self.recv(client))['Name']
                    if cName is False:
                        continue

                    self.socket_list.append(client)

                    self.window.textEdit_update(text = f"Got a new connection {client.fileno()} from {cName} :- {address} ")
                    self.clientMap[client] = {"Name" : cName,'Address' : address}
                    self.window.updateTable(True,cName,address[0],address[1])
                    self.outputs.append(client)

                else:
                    message = self.recv(sock)

                    if message is False:
                        self.outputs.remove(sock)
                        cName = self.getName(sock)
                        add = self.getAdd(sock)

                        self.window.textEdit_update(color = 'red', text = f'Client {cName} disconnected % {add}')

                        if sock in self.socket_list: self.socket_list.remove(sock)

                        if sock in self.clientMap: del self.clientMap[sock]

                        self.window.updateTable(False,cName,add[0],add[1])

                        continue

                    self.window.textEdit_update(text = f"Received message from {message['Name']} : {message['msg']}")
                    self.send(sock,Name = 'Server',msg = 'Hello')

            for sock in error:
                if sock in self.socket_list: self.socket_list.remove(sock)
                if sock in self.clientMap: del self.clientMap[sock]

                        
