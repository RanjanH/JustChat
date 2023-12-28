import socket
import sys
import errno
import dotenv
import os
import pickle
import struct

dotenv.load_dotenv()

marshall = pickle.dumps

HEADER_LENGTH = 10

IP = os.getenv("IP")
PORT = int(os.getenv("PORT"))
my_username = input("Username: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

client_socket.setblocking(False)

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
#client_socket.send(username_header + username)

def send(channel,**msg):
    buffer = marshall(msg)
    value = socket.htonl(len(buffer))
    size = struct.pack("L",value)
    channel.send(size + buffer)

send(client_socket,Name = my_username)

while True:
    message = input(f'{my_username} > ')
    if message:
        '''message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)'''
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
        sys.exit()