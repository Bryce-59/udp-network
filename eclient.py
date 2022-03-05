# TODO: finish implementing the event-loop using pyuv

# import main_client
# from main_client import *
import random
from message import *
import socket
from socket import *
import sys
import threading
from threading import *
import pyuv

seq_num = 1

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
    # TODO: set up so it works with pyuv instead of whatever its doing now
    global seq_num
    data = sys.stdin.readline()
    if (not data or (data == "q\n" and sys.stdin.isatty())):
        rcv_cmd = send(Command.GOODBYE, seq_num, session_id, None)
        close_session()
    else:
        message = pack_message(Command.DATA, seq_num, session_id, data)
        clientSocket.sendto(message,(serverName, serverPort))
    seq_num += 1

def handle_socket():
    # TODO: set up so it works with pyuv instead of whatever its doing now
    timer = threading.Timer(5, close_session)
    timer.start()
    magic, version, command, sequence, session_id, data = receive()
    timer.cancel()
    if (command == Command.GOODBYE):
        print('closing client')
    if (command != Command.ALIVE):
        close_session()

# check the next three functions for code that needs to be changed to pyuv
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
    shutdown_time.set()

if __name__ == '__main__':
    serverName = gethostbyname("descartes.cs.utexas.edu")
    serverPort = 5000
    
    session_id = random.randint(0x00000000, 0xFFFFFFFF)

    # Set up the event loop
    loop = pyuv.Loop.default_loop()
    client  = pyuv.UDP(loop)
    clientTTY = pyuv.TTY(loop, sys.stdin.fileno(), True)
    Timer = pyuv.Timer(loop)

    # Handshake start
    firstPacket = pack_message(Command.HELLO, 0, session_id)
    client.start_recv(handle_keyboard)
    client.send((serverName, serverPort), firstPacket)

    # Start the event loop
    Timer.start(close_session, 5.0, 0)
    clientTTY.start_read(handle_socket)
    
    loop.run()

    # Wait for shutdown and close out
    exit()
