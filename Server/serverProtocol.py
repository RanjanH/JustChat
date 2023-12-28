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
                        


'''def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False

while True:

    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)
            clients[client_socket] = user
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        else:
            message = receive_message(notified_socket)

            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]

                continue

            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]'''