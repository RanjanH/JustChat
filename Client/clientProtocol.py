import socket
import sys
import errno
import dotenv
import os
import pickle
import struct

from time import strftime,localtime

dotenv.load_dotenv()

marshall = pickle.dumps
unmarshall = pickle.loads


class ClientProtocol:
    def __init__(self):
        self.uName = ''
        self.IP = os.getenv("IP")
        self.PORT= int(os.getenv("PORT"))
        self.client_socket = ''
        self.window = ''

    def timed(self):
        return strftime("%H:%M:%S",localtime())

    def formatResult(self,color = 'black',text = ''):
        return f"<font color = '{color}'>[{self.timed()}] * {text}</font>"

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
    
    def connect(self):
        print("Connecting")

        self.window.setWindowTitle(f'{self.uName} Just Chat!')
        self.window.chatView_update(color = 'blue', text = 'Connecting....')
        if self.uName == '':
            self.window.name()
        print("HUH!!")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.IP, self.PORT))
        except:
            self.window.chatView_update(color = "red", text = "Failed to connect to server")

        self.client_socket.setblocking(False)

        self.send(self.client_socket,Name = self.uName)

        self.window.chatView_update(color = 'green',text = 'Connected to Server!!')

'''while True:
    message = input(f'{my_username} > ')
    if message:
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
        send(client_socket,Name = my_username,msg = message)

    try:
        while True:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            print(f'{username} > {message}')

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        continue

    except Exception as e:
        print('Reading error: '.format(str(e)))
        sys.exit()'''