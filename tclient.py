# TODO: Client should stop accepting input when it shuts down due to timeout
# TODO: Client should be able to timeout when in handshake (currently does not work)
# TODO: Client should check magic number, version number, and session_id when receiving packages

# import main_client
# from main_client import *
import random
from message import *
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
    shutdown_time.set()

if __name__ == '__main__':
    session_id = random.randint(0x00000000, 0xFFFFFFFF)

    # Handshake start
    send(Command.HELLO, 0, session_id)
    timer = threading.Timer(5, close_session)
    timer.start()
    _, _, command, _, _, _ = receive()
    timer.cancel()

    if (command != Command.HELLO):
        close_session()

    # Start the main function
    t1 = Thread(target=handle_socket, daemon=True)
    t2 = Thread(target=handle_keyboard, args=(session_id,), daemon=True)
    t1.start()
    t2.start()

    # Wait for shutdown and close out
    shutdown_time.wait()
    close_session()
