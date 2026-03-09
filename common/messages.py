from enum import Enum

class ClientMessage(str, Enum):
    HELLO = "HELLO"
    DISCONNECT = "!DISCONNECT"
    CHAT = "CHAT"

class ServerMessage(str, Enum):
    HELLO_OK = "HELLO_OK"
    HELLO_ERR_INVALID_HELLO = "HELLO_ERR:INVALID_HELLO"
    HELLO_ERR_INVALID_USERNAME = "HELLO_ERR:INVALID_USERNAME"
    HELLO_ERR_USERNAME_TAKEN = "HELLO_ERR:USERNAME_TAKEN"
    USER_LIST = "USER_LIST"

class DiffieHellmanMessage(str, Enum):
    DH_INIT = "DH_INIT"
    DH_RESPONSE = "DH_RESPONSE"

def build_hello(username):
    return f"{ClientMessage.HELLO.value}:{username}"

def build_server_user_list(users):
    return f"{ServerMessage.USER_LIST.value}:{users}"

def build_chat(target, username, encrypted_message):
    return f"{ClientMessage.CHAT.value}:{target}:{username}:{encrypted_message}"

def parse_hello(payload):
    prefix = f"{ClientMessage.HELLO.value}:"
    if not payload or not payload.startswith(prefix):
        return None
    return payload.split(":", 1)[1].strip()

def parse_server_user_list(payload):
    prefix = f"{ServerMessage.USER_LIST.value}:"
    if not payload or not payload.startswith(prefix):
        return None
    return payload.split(":", 1)[1].strip().split(" ")

def parse_chat(payload):
    prefix = f"{ClientMessage.CHAT.value}:"
    if not payload or not payload.startswith(prefix):
        return None
    data = payload.split(":",3)
    target = data[1].strip()
    username = data[2].strip()
    encrypted_message = data[3].strip()
    return target, username, encrypted_message

# format: DH_INIT:target:sender:pubkey
#      ili DH_RESPONSE:target:sender:pubkey

def parse_dh_target(payload):
    parts = payload.split(":", 3)
    if len(parts) < 2:
        return None
    return parts[1].strip()

def parse_dh_sender(payload):
    parts = payload.split(":", 3)
    if len(parts) < 3:
        return None
    return parts[2].strip()

def parse_dh_public_key(payload):
    parts = payload.split(":", 3)
    if len(parts) < 4:
        return None
    return int(parts[3].strip())