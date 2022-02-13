from socket import *
from message import *

session_list = []
sequence_list = []

def verify_session(message):
    valid, cmd, seq, s_id, data = message_unpacking(message)
    if (valid == False):
        return None, None, None #close
    
    if (s_id not in session_list):
        if (cmd == Command.HELLO):
            if (seq == 0):
                session_list.append(s_id)
                sequence_list.append(seq)
                return cmd, s_id, data
            else:
                return None, None, None #close immediately, no messages
        else:
            return None, None, None #terminates
    else:
        value = sequence_list[session_list.index(s_id)]
        if (seq == value + 1):
            sequence_list[session_list.index(s_id)] += 1
            return cmd, s_id, data
        else:
            if (seq > value):
                return None, None, None #"Lost packet!"
            if (seq == value):
                return None, None, None #"Duplicate packet!" (discard)
            else:
                return None, None, None #protocol error (GOODBYE)

if __name__ == '__main__':

    serverPort = 5000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    print('ready to serve')

    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        '''
        * header length is constant
        * query socket library for the length of the upd segment/packet?

        - figure out what kind of message we were sent

        TEST: using just data option, return error if not data command
        '''
        # modifiedMessage = message.decode().upper()
        print(message)
        command, session_id, data = verify_session(message) # THIS IS THE FUNCTION I ADDED, feel free to do whatever with it
        # print(type(message))
        print(command)
        # serverSocket.sendto(modifiedMessage.encode(), clientAddress)
