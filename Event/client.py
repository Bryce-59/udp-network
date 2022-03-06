from enum import IntEnum
import random
from packet import *
import socket
from socket import *
import sys
import threading
from threading import *
import pyuv

# TODO: Finish Event-loop client

# vvv READ THIS vvv
# NOTE: You have to enter the server and the portnumber into the commandline as arguments now.
# For example, $python3 client.py aristotle.cs.utexas.edu 5000
# Similarly, for the server, you have to do the portnumber i.e. $python3 5000
# ^^^ READ THIS ^^^

serverName = None
serverPort = None
SESSION_ID = random.randint(0x00000000, 0xFFFFFFFF)

class FSA(IntEnum):
    HELLO = 0
    HELLO_WAIT = 1
    READY = 2
    READY_TIME = 3
    CLOSING = 4
    CLOSED = 5

FSA = FSA.HELLO
seq_num = 0

def receivePacket(handle, ip_port, flags, data, error):
    global FSA
    packet = data
    if len(packet) >= MIN_SIZE:
        magic, version, command, _, rcv_id, _ = unwrap_packet(packet)
        if magic == MAGIC and version == VERSION and rcv_id == SESSION_ID:
            if SESSION_ID == rcv_id:
                if FSA == FSA.HELLO_WAIT and command == Command.HELLO:
                    FSA = FSA.READY
                elif FSA == FSA.READY or FSA == FSA.READY_TIME:
                    if (command == Command.GOODBYE):
                        print('closing client')
                        goodbyeAsync.send()
                    elif (command == Command.ALIVE):
                        Timer.stop()
                        FSA = FSA.READY
                        pass
                else:
                    goodbyeAsync.send()

def on_tty_read(handle, data, error):
    data_str = data.decode("UTF-8")
    global FSA
    global seq_num
    if (not data_str or data_str == "q\n"): #sys.stdin may not be correct here
        packet = wrap_packet(Command.GOODBYE, seq_num, SESSION_ID, data)
        client.send((serverName, serverPort),packet)
        goodbyeAsync.send()
    
    packet = wrap_packet(Command.DATA, seq_num, SESSION_ID, data)
    client.send((serverName, serverPort),packet)
    if FSA == FSA.READY:
        Timer.start(close_session,5,5)
        FSA = FSA.READY_TIME
    seq_num += 1

def emptyEvent_func(handle=None):
    pass

def close_session(handle=None):
    clientTTY.stop_read()
    client.stop_recv()
    Timer.stop()
    loop.stop()
    # endLoopAsync.send()

'''def TimerGoodbye():
    close_session()
    pass'''

if __name__ == '__main__':
    serverName = gethostbyname(sys.argv[1])
    serverPort = int(sys.argv[2])
    
    loop = pyuv.Loop.default_loop()
    client = pyuv.UDP(loop)
    clientTTY = pyuv.TTY(loop, sys.stdin.fileno(), True)
    Timer = pyuv.Timer(loop)

    goodbyeAsync = pyuv.Async(loop, close_session)
    endLoopAsync = pyuv.Async(loop, emptyEvent_func)

    #starting the session
    SESSION_ID = random.randint(0x00000000, 0xFFFFFFFF)

    #sending the first packet and starting the connection
    firstPacket = wrap_packet(Command.HELLO, seq_num, SESSION_ID)
    FSA = FSA.HELLO_WAIT
    client.start_recv(receivePacket)
    client.send((serverName, serverPort), firstPacket)
    seq_num += 1

    Timer.start(close_session,5,5)

    #start reading input
    clientTTY.start_read(on_tty_read)

    #start the loop
    loop.run()
    exit()