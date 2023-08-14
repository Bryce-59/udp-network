# About the Project
A program created in 2022 to simulate a (potentially lossy) UDP connection. 

There are two variants: The Thread client/server, which uses multi-threading to execute the program; 
and the Event client, which uses an Event-Loop implemented with the `pyuv` library.

# How to Use
Navigate to the Thread or Event directory. There, execute the server with `python3 ./server.py <port_number>`
to create a server at the specified port. Then, execute a client with `python3 ./client.py <host_name> <port_number>`. 
Messages can be sent from the client to the server via keyboard input, or from a file with the "<" operator. The client will time-out if no input is entered.

In addition, tests and test files can be found in the Thread/Test directory or in the Event/Test directory.

# Credits
- 2022 Bryce Richardson (lead)
- 2022 Tyler Miller