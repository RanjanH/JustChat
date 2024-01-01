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
        self.rooms = {}
        self.STATE = True
        self.socket_list = []
        self.clientMap = {}
        self.outputs = []
        self.server_key = ''
        self.server_pubKey = ''
        self.window = ''
        self.commands = ['/create','/join','/leave']

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

    def sendMsg(self,channel,text):
        self.send(channel,Name = 'Server',msg = text)

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
    
    def createRoom(self,sock,rName):
        if rName in self.rooms.keys():
            self.sendMsg(sock,f"Room {rName} already exists. Why don't you try joining it?")
            return
        self.rooms[rName] = []
        self.rooms[rName].append(sock)
        self.sendMsg(sock,f"Room {rName} is created.")
        self.window.textEdit_update(color = 'brown',text = f'New room {rName} created by {self.getName(sock)}')

    def join(self,sock,rName):
        self.rooms[rName].append(sock)
        self.sendMsg(sock,f"Room {rName} joined!")
        self.window.textEdit_update(color = 'brown',text = f'Room {rName} joined by {self.getName(sock)}')
        online = ''
        for i in self.rooms[rName]:
            if i != sock:
                self.send(i,Name = 'Server',msg = f"Online:{self.getName(sock)}",To = rName)
                online += self.getName(i) + ' '
        self.send(sock, Name = 'Server', msg = "Online:" + online, To = rName)
        
    
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

                    self.sendMsg(client,f'Welcome to The server {cName}!')
                    self.sendMsg(client,"Following are some commands which you can use in the server room :-")
                    self.sendMsg(client," --- /create <room name> :> Create a new room, The room name should have no spaces.")
                    self.sendMsg(client," --- /join <room name> :> Join a room.")
                    self.sendMsg(client," --- /leave <room name> :> Leave a room.")

                    if len(self.rooms) > 0:
                        self.sendMsg(client,f'Following are the list of active rooms that you can join :-')
                        for i in self.rooms.keys():
                            self.sendMsg(client,f' --- {i}')
                    else:
                        self.sendMsg(client,"Currently there are no rooms why don't you be the first to create a room")

                else:
                    message = self.recv(sock)
                    print(message)

                    if message is False:
                        self.outputs.remove(sock)
                        cName = self.getName(sock)
                        add = self.getAdd(sock)

                        self.window.textEdit_update(color = 'red', text = f'Client {cName} disconnected % {add}')

                        if sock in self.socket_list: self.socket_list.remove(sock)

                        if sock in self.clientMap: del self.clientMap[sock]

                        self.window.updateTable(False,cName,add[0],add[1])

                        continue

                    self.window.textEdit_update(text = f"Received message from {message['Name']} for {message['To']} : {message['msg']}")
                    if message['To'] == 'Server':
                        if (message['msg'].split())[0] not in self.commands:
                            self.sendMsg(sock,'Not a valid command. Use lower case for command. The room name can be in any format.')
                            continue
                        cmd = (message['msg'].split())[0]
                        rName = (message['msg'].split())[1]
                        if cmd == '/create':
                            self.createRoom(sock,rName)
                        elif len(self.rooms) == 0 and (cmd == '/leave' or cmd == '/join'):
                            self.sendMsg(sock,f'No such Room found for you to {rName}')
                        elif cmd == '/join':
                            self.join(sock,rName)
                        else:
                            if cmd == '/leave':
                                try:
                                    self.rooms[rName].remove(sock)
                                    self.sendMsg(sock,f'You left room {rName}')
                                    for i in self.rooms[rName]:
                                        self.send(i,Name = 'Server',msg = f'{self.getName(sock)} left the room {rName}',To = rName)
                                except:
                                    self.sendMsg(sock,f'You have not joined room {rName}')
                    else:
                        for i in self.rooms.keys():
                            if i == message['To']:
                                for j in self.rooms[i]:
                                    if j != sock:
                                        self.send(j,Name = message['Name'],msg = message['msg'],To = message['To'])

            for sock in error:
                if sock in self.socket_list: self.socket_list.remove(sock)
                if sock in self.clientMap: del self.clientMap[sock]

                        
