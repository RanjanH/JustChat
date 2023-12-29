import socket
import errno
import sys
import pickle
import struct
import dotenv
import os

from random import randint
from time import strftime,localtime,sleep

dotenv.load_dotenv()

marshall = pickle.dumps
unmarshall = pickle.loads

class ClientProtocol:
    def __init__(self):
        self.connected = False
        self.IP = os.getenv('IP')
        self.PORT = int(os.getenv('PORT'))
        self.uName = f"User{randint(1000,9999)}"
        self.client_socket = ''
        self.window = ''

    def timed(self):
        return strftime("%H:%M:%S",localtime())

    def formatResult(self,color = 'black',text = ''):
        return f"<font color = '{color}'>[{self.timed()}] * {text}</font>"

    def send(self,channel,**kw):
        buffer = marshall(kw)
        value = socket.htonl(len(buffer))
        size = struct.pack("L",value)
        channel.send(size + buffer)

    def recv(self,sock):
        size = struct.calcsize("L")
        size = sock.recv(size)
        try:
            size = socket.ntohl(struct.unpack("L",size)[0])
        except struct.error as e:
            return ''
        '''except :
            return False'''
        
        buffer = ''
        while len(buffer) < size:
            buffer = sock.recv(size - len(buffer))
        buffer = unmarshall(buffer)
        return buffer

    def connect(self):
        sleep(1)
        self.window.emitSignal(color = 'blue', text = 'Connecting....',newOnline = False)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.IP, self.PORT))
        except:
            self.window.emitSignal(color = "red", text = "Failed to connect to server",newOnline = False)
            return
        
        self.connected = True
        self.client_socket.setblocking(False)

        self.send(self.client_socket,Name = self.uName)

        self.window.emitSignal(color = 'green',text = 'Connected to Server!!',newOnline = False)

        self.handler()

    def sendMsg(self,msgs):
        self.send(self.client_socket,Name = self.uName,msg = msgs)

    def handler(self):
        while True:
            try:
                while True:
                    msg = self.recv(self.client_socket)
                    if not len(msg):
                        print('Connection closed by the server')
                        sys.exit()
                    print(f'{msg["Name"]} > {msg["msg"]}')

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()
                continue

            except Exception as e:
                print('Reading error: '.format(str(e)))
                sys.exit()