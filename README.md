# About the Project
A program created in 2022 to simulate a (potentially lossy) UDP connection in a Linux enviornment. 

There are two variants: The Thread client/server, which uses multi-threading to execute the program; 
and the Event client, which uses an Event-Loop implemented with the `pyuv` library.

# How to Use
First, execute the server with `python3 ./server.py $(PORT)` to create a server at the specified port. Then, execute a Thread client with `python3 ./client.py $(HOST) $(PORT)`. 
Messages can be sent from the client to the server via keyboard input, or from a file with the "<" operator. The client will exit when "q" is entered or if no input is entered after five seconds.

In addition, tests and test files can be found in the Test directory. The crazy client/server are models which send improper messages and can be used to test the main client/server. The "crazy messages" must be manually set.

> :warning: **Project is only guaranteed to work in a Linux enviornment!**

# Credits
- 2022 Bryce Richardson (lead)
- 2022 Tyler Miller