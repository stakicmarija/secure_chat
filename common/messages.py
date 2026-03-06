from enum import Enum

class ClientMessage(str, Enum):
    HELLO = "HELLO"
    DISCONNECT = "!DISCONNECT"

class ServerMessage(str, Enum):
    HELLO_OK = "HELLO_OK"
    HELLO_ERR_INVALID_HELLO = "HELLO_ERR:INVALID_HELLO"
    HELLO_ERR_INVALID_USERNAME = "HELLO_ERR:INVALID_USERNAME"
    HELLO_ERR_USERNAME_TAKEN = "HELLO_ERR:USERNAME_TAKEN"

def build_hello(username):
    return f"{ClientMessage.HELLO.value}:{username}"

def parse_hello(payload):
    prefix = f"{ClientMessage.HELLO.value}:"
    if not payload or not payload.startswith(prefix):
        return None
    return payload.split(":", 1)[1].strip()
