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

class FSA(IntEnum):
    HELLO = 0
    HELLO_WAIT = 1

FSA = FSA.HELLO
seq_num = 0

def receivePacket(handle, ip_port, flags, data, error):
    magic, version, command, sequence, session_id, data = unwrap_packet(data)
    if (FSA == FSA.HELLO_WAIT):
        # check if command == HELLO
        pass
    elif (True): # check if in ready state
        # reset timer if ALIVE, close out if GOODBYE, else protocol error
        pass
    # protocol error

def on_tty_read(handle, data, error):
    if (not data or (data == "q\n" and sys.stdin.isatty())): #sys.stdin may not be correct here
        # close out
        pass
    # else wrap and send the data

def TimerGoodbye():
    # close out
    pass

if __name__ == '__main__':
    address = gethostbyname("descartes.cs.utexas.edu")
    portNum = 5000
    loop = pyuv.Loop.default_loop()
    client = pyuv.UDP(loop)
    clientTTY = pyuv.TTY(loop, sys.stdin.fileno(), True)
    Timer = pyuv.Timer(loop)
    # endLoopAsync = pyuv.Async(loop, noCallback)

    #starting the session
    SESSION_ID = random.randint(0x00000000, 0xFFFFFFFF)

    #sending the first packet and starting the connection
    firstPacket = wrap_packet(Command.HELLO, seq_num, SESSION_ID)
    client.start_recv(receivePacket)
    client.send((address, portNum), firstPacket)
    
    FSA = FSA.HELLO_WAIT
    Timer.start(TimerGoodbye, 5.0, 0)

    #start reading input
    clientTTY.start_read(on_tty_read)

    #start the loop
    loop.run()
    exit()