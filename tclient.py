# TODO: Client should check magic number, version number, and session_id when receiving packages
# TODO: close_session does not work (for some reason-- this is why timeout fails)

# import main_client
# from main_client import *
import random
from message import *
import socket
from socket import *
import sys
import threading
from threading import *

import os

serverName = 'descartes.cs.utexas.edu'
serverPort = 5000
clientSocket = socket(AF_INET, SOCK_DGRAM)
shutdown_time = threading.Event()
timer = None

def send(command, seq_num, session_id, data=None):
    message = pack_message(command, seq_num, session_id, data)
    clientSocket.sendto(message,(serverName, serverPort))
    try:
        timer.start()
    except:
        pass

def receive():
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    timer.cancel()
    return unpack_message(modifiedMessage)

def close_session():
    try:
        clientSocket.shutdown(SHUT_WR)
    except:
        pass
    clientSocket.close()
    # exit()
    os._exit(0)

def handle_keyboard(session_id):
    seq_num = 1
    while True:
        data = sys.stdin.readline()
        if (not data or (data == "q\n" and sys.stdin.isatty())):
            send(Command.GOODBYE, seq_num, session_id, None)
            break
        else:
            send(Command.DATA, seq_num, session_id, data)
        seq_num += 1
    shutdown_time.set()

def handle_socket():
    while True:
        magic, version, command, sequence, session_id, data = receive()
        if (command == Command.GOODBYE):
            print('closing client')
        if (command != Command.ALIVE):
            break
    shutdown_time.set()

if __name__ == '__main__':
    session_id = random.randint(0x00000000, 0xFFFFFFFF)
    timer = threading.Timer(5, close_session)
    timer.start()

    # Handshake start
    send(Command.HELLO, 0, session_id)
    _, _, command, _, _, _ = receive()

    if (command == Command.HELLO):
        # Start the main function
        t1 = Thread(target=handle_socket, daemon=True)
        t2 = Thread(target=handle_keyboard, args=(session_id,), daemon=True)
        t1.start()
        t2.start()

        # Wait for shutdown and close out
        shutdown_time.wait()
    close_session()
