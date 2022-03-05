'''from message import *
import socket
from socket import *
import sys
import threading
from threading import *

serverName = 'descartes.cs.utexas.edu'
serverPort = 5000
clientSocket = socket(AF_INET, SOCK_DGRAM)
shutdown_time = threading.Event()

def send(command, seq_num, session_id, data=None):
    message = pack_message(command, seq_num, session_id, data)
    clientSocket.sendto(message,(serverName, serverPort))

def receive():
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    return unpack_message(modifiedMessage)

def close_session():
    try:
        clientSocket.shutdown(SHUT_WR)
        clientSocket.close()
    except:
        pass
    exit()

def handle_keyboard(session_id):
    seq_num = 1
    while True:
        data = sys.stdin.readline()
        if (not data or (data == "q\n" and sys.stdin.isatty())):
            rcv_cmd = send(Command.GOODBYE, seq_num, session_id, None)
            break
        else:
            message = pack_message(Command.DATA, seq_num, session_id, data)
            clientSocket.sendto(message,(serverName, serverPort))
        seq_num += 1
    shutdown_time.set()

def handle_socket():
    while True:
        timer = threading.Timer(5, close_session)
        timer.start()
        magic, version, command, sequence, session_id, data = receive()
        timer.cancel()
        if (command == Command.GOODBYE):
            print('closing client')
        if (command != Command.ALIVE):
            break
    shutdown_time.set()'''