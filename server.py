#TODO: Implement GOODBYE
#TODO: Implement Error Handling
#TODO: Add threads: ONE should listen for messages, TWO should accept keyboard inputs 

from socket import *
from message import *

session_list = []
sequence_list = []

"""
A function that accepts a message and then ensures that it is a
valid session. This involves checking the session_id and sequence_number.
"""
def verify_session(message):
    valid, cmd, seq, s_id, data = message_unpacking(message)
    if (valid == False):
        print("invalid")
        return None, None, None #close
    if (s_id not in session_list):
        if (cmd == Command.HELLO):
            if (seq == 0):
                session_list.append(s_id)
                sequence_list.append(seq)
                return cmd, s_id, data
            else:
                print("Hello, not 0")
                return None, None, None #close immediately, no messages
        else:
            print("0, not Hello")
            return None, None, None #terminates
    else:
        value = sequence_list[session_list.index(s_id)]
        if (seq == value + 1):
            sequence_list[session_list.index(s_id)] += 1
            return cmd, s_id, data
        else:
            if (seq > value):
                print("Lost packet")
                return None, None, None #"Lost packet!"
            if (seq == value):
                print("Duplicate packet")
                return None, None, None #"Duplicate packet!" (discard)
            else:
                print("Goodbye (bad)")
                return None, None, None #protocol error (GOODBYE)

if __name__ == '__main__':

    serverPort = 5000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    print('ready to serve')

    global_counter = 0

    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        command, session_id, data = verify_session(message)
        
        "Handshake Start"
        if (command == Command.HELLO):
            message = message_packing(Command.HELLO, global_counter, session_id)
            serverSocket.sendto(message, clientAddress)
            global_counter += 1
            "Handshake End"
        if (command == Command.DATA):
            print(data.decode(encoding='ASCII'))
            message = message_packing(Command.ALIVE, global_counter, session_id)
            serverSocket.sendto(message, clientAddress)
            global_counter += 1


        '''
        * header length is constant
        * query socket library for the length of the upd segment/packet?

        - figure out what kind of message we were sent

        TEST: using just data option, return error if not data command
        '''
