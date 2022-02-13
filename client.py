from socket import *
import random
from message import *

serverName = 'aristotle.cs.utexas.edu' #ALWAYS CHECK BEFORE RUNNING
serverPort = 5000
clientSocket = socket(AF_INET, SOCK_DGRAM)
session_id = random.randint(0,(2**31) - 1)

def send_and_receive(command, seq_num, data=None):
    message = message_packing(command, seq_num, session_id)
    if (command == Command.DATA):
        message = b''.join((message, data.encode('ASCII')))
    clientSocket.sendto(message,(serverName, serverPort))
    
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    valid, rcv_cmd, _, _, _ = message_unpacking(modifiedMessage)
    return rcv_cmd

if __name__ == '__main__':
    seq_num = 0

    "Handshake Start"
    rcv_cmd = send_and_receive(Command.HELLO, seq_num)
    seq_num += 1
    if (rcv_cmd != Command.HELLO):
        #terminate
        print("error") #delete
    "End Handshake"

    while (True): #Implement so that server returns ALIVE after receiving DATA 
        data = input('Input message: ')

        rcv_cmd = send_and_receive(Command.DATA, seq_num, data)
        seq_num += 1

        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        print(modifiedMessage.decode())

    clientSocket.close()
