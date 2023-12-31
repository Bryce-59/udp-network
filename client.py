#!/usr/bin/env python3 

import random
from socket import *
import threading
import sys

from fsa_client import FSA
from packet import *

clientSocket = socket(AF_INET, SOCK_DGRAM)
shutdown_time = threading.Event()
serverName = None
serverPort = None
SESSION_ID = random.randint(0x00000000, 0xFFFFFFFF)
seq_num = 0
FSA = FSA.HELLO
timer = None

'''
Helper function that sends a command to the specified server
'''
def send(command, data=None):
    global seq_num
    packet = wrap_packet(command, seq_num, SESSION_ID, data)
    clientSocket.sendto(packet,(serverName, serverPort))
    seq_num += 1


'''
Corner cases -
    Ignore   | packet < 12 bytes (not P0P packet)
    Ignore   | magic != MAGIC or version != VERSION
    
    Goodbye  | server sends incorrect session id
    Goodbye  | no FSA (i.e. not expected command and not GOODBYE)

    Ignore   | server sends ALIVE when requested GOODBYE
'''
def request(expected):
    while True:
        packet, serverAddress = clientSocket.recvfrom(2048)
        if len(packet) >= MIN_SIZE:
            magic, version, command, sequence, rcv_id, data = unwrap_packet(packet)
            if magic == MAGIC and version == VERSION: 
                if not SESSION_ID == rcv_id:
                    return False
                if command == Command.GOODBYE:
                    timer.cancel()
                    close_client()
                elif command == expected:
                    return True
                elif FSA != FSA.CLOSING and command != Command.ALIVE:
                    return False

'''
Start the code
'''
def open_client():
    global timer
    global FSA
    timer = threading.Timer(5, prepare_to_close)
    send(Command.HELLO, None)
    FSA = FSA.HELLO_WAIT
    timer.start()
    hello = request(Command.HELLO)
    timer.cancel()
    if hello:
        FSA = FSA.READY

        # Start the main running threads
        t1 = threading.Thread(target=handle_socket, daemon=False)
        t2 = threading.Thread(target=handle_keyboard, daemon=False)
        t1.start()
        t2.start()
    else:
        prepare_to_close(error=True)

def prepare_to_close(error=False):
    global timer
    global FSA
    timer.cancel()
    if not FSA == FSA.CLOSING: 
        FSA = FSA.CLOSING
        send(Command.GOODBYE, None)
    
    if not error:
        timer = threading.Timer(5, close_client)
        timer.start()
        request(Command.GOODBYE)
        timer.cancel()
    
    close_client()


'''
Enter the CLOSING phase and transition to CLOSED
based on server response
'''
def close_client():
    shutdown_time.set()

'''
The main socket loop
'''
def handle_socket():
    global FSA
    while True:
        alive = request(Command.ALIVE)
        
        if alive:
            if FSA == FSA.READY_TIME:
                timer.cancel()
                FSA = FSA.READY
        else:
            break
    prepare_to_close(error=True)

'''
The main input loop
'''
def handle_keyboard():
    global timer
    global FSA
    while True:
        data = sys.stdin.readline()
        if not data or (data == "q\n" and sys.stdin.isatty()):
            if not data:
                print("eof")
            prepare_to_close()
            break
        else:
            send(Command.DATA, data.encode('UTF-8'))
            if FSA == FSA.READY:
                timer = threading.Timer(5, prepare_to_close)
                FSA = FSA.READY_TIME
                timer.start()

if __name__ == '__main__':
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    
    # Start (HELLO_WAIT, READY/READY_TIME)
    t_start = threading.Thread(target=open_client, daemon=False)
    t_start.start()

    # Wait to shut down 
    shutdown_time.wait()
    try:
        clientSocket.shutdown(SHUT_WR)
    except:
        pass
    clientSocket.close()
    FSA = FSA.CLOSED