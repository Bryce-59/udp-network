from enum import IntEnum

'''
An enum class to represent the Finite State Automata (FSA) of the session on the client side.
'''
class FSA(IntEnum):
    HELLO = 0
    HELLO_WAIT = 1
    READY = 2
    READY_TIME = 3
    CLOSING = 4
    CLOSED = 5