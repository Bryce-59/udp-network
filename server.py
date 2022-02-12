from socket import *

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
        print(type(message))
        print(message)
        # serverSocket.sendto(modifiedMessage.encode(), clientAddress)
