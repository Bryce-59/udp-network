from socket import *

session_list = []
sequence_list = []

def message_checking(message): #rough skeleton for message_checking function (ERRORS NOT IMPLEMENTED)
    magic = int.from_bytes(message[:2],byteorder='big')
    version = int.from_bytes(message[2:3],byteorder='big')
    if (m != 0xC356 or v != 1): #if magic or version numbers are wrong, should be "silently discarded" (invalid)
        return None
    
    cmd = int.from_bytes(message[3:4],byteorder='big')
    seq = int.from_bytes(message[4:8],byteorder='big')
    ses_id = int.from_bytes(message[8:12],byteorder='big')
    data = message[12:]

    if (ses_id not in session_list): #check if pre-existing ses_id or not
        if (cmd == 0 and seq == 0): #if HELLO and new ses_id, add to the lists (valid)
            session_list.append(ses_id)
            sequence_list.append(seq)
            return cmd, data
        else: #something went wrong (invalid)
            return None #terminates if seq == 0 and cmd != HELLO, close immediately with no messages if cmd == HELLO and seq != 0
    else:
        if (seq != sequence_list[session_list.index(si)] + 1): #check if correct seq for the ses_id 
            return None #"Lost packet!" if greater, "Duplicate packet" (and discarded) if one less, and protocol error if many less (GOODBYE and close)
        else:
            sequence_list[session_list.index(si)] += 1 #increment the seq by 1
            return cmd, data

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
        command, data = message_checking(message) # THIS IS THE FUNCTION I ADDED, feel free to do whatever with it
        # print(type(message))
        print(command)
        # serverSocket.sendto(modifiedMessage.encode(), clientAddress)
