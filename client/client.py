import socket
import threading

from common.config import ADDR, QUIT_COMMAND, CHAT_COMMAND
from common.messages import ClientMessage, ServerMessage, build_hello, parse_server_user_list,\
    DiffieHellmanMessage, parse_dh_sender, parse_dh_public_key
from common.protocol import recv_packet, send_packet
from common.cryptography import generate_private_key, generate_public_key, generate_session_key


class Client:

    def __init__(self, addr):
        self.addr = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.stop_event = threading.Event()
        self.receiver_thread = None
        self.active_clients = []
        self.chats_with = None
        self.dh_private = None
        self.session_key = None

    def connect(self):
        self.socket.connect(self.addr)

    def handshake(self):
        username = input("Enter username: ").strip()

        while not username:
            username = input("Username cannot be empty. Enter username: ").strip()

        send_packet(self.socket, build_hello(username))
        response = recv_packet(self.socket)

        if response != ServerMessage.HELLO_OK.value:
            print(f"Server rejected connection: {response}")
            return False

        self.username = username
        print("Username accepted.")
        print(f"Use {QUIT_COMMAND} to disconnect.")
        print(f"Use {CHAT_COMMAND} username to chat.")
        return True

    def start_session(self, target, init):
        private_key = generate_private_key()
        public_key = generate_public_key(private_key)
        self.chats_with = target
        self.dh_private = private_key
        if init:
            send_packet(self.socket, f"{DiffieHellmanMessage.DH_INIT.value}:{target}:{self.username}:{public_key}")
        else:
            send_packet(self.socket, f"{DiffieHellmanMessage.DH_RESPONSE.value}:{target}:{self.username}:{public_key}")

    def receive_loop(self):
        while not self.stop_event.is_set():
            try:
                message = recv_packet(self.socket)

                if message is None:
                    print("[SYSTEM] Connection to server was lost. Press Enter to exit.")
                    self.stop_event.set()
                    break

                elif message.startswith(ServerMessage.USER_LIST.value):
                    self.active_clients = parse_server_user_list(message)
                    print(f"[SYSTEM] Active users: {', '.join(self.active_clients)}")

                elif message.startswith(DiffieHellmanMessage.DH_INIT.value):
                    sender = parse_dh_sender(message)
                    user_dh_public = parse_dh_public_key(message)
                    print(f"\n[SYSTEM] {sender} wants to start a secure session. Accepting...")
                    self.start_session(sender, False)
                    self.session_key = generate_session_key(user_dh_public, self.dh_private)
                    print(f"[SYSTEM] Secure session established with {sender}.")

                elif message.startswith(DiffieHellmanMessage.DH_RESPONSE.value):
                    sender = parse_dh_sender(message)
                    user_dh_public = parse_dh_public_key(message)
                    if sender == self.chats_with:
                        self.session_key = generate_session_key(user_dh_public, self.dh_private)
                        print(f"[SYSTEM] Secure session established with {sender}.")

                else:
                    print(f"\n{message}")

            except Exception as exc:
                if not self.stop_event.is_set():
                    print(f"[SYSTEM] Error while receiving message: {exc}")
                self.stop_event.set()
                break

    def start_receiver(self):
        self.receiver_thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.receiver_thread.start()

    def input_loop(self):
        while not self.stop_event.is_set():
            text = input()

            if text == QUIT_COMMAND:
                send_packet(self.socket, ClientMessage.DISCONNECT.value)
                self.stop_event.set()
                break

            elif text.startswith(CHAT_COMMAND):
                msg = text.split(" ")
                if len(msg) < 2 or not msg[1].strip():
                    print("Usage: /chat <username>")
                elif len(msg) > 2:
                    print("Choose only one user")
                elif msg[1] not in self.active_clients:
                    print("User doesn't exist")
                elif msg[1] == self.username:
                    print("You cannot chat with yourself")
                else:
                    print(f"Starting session with {msg[1]}...")
                    self.start_session(msg[1], True)

            elif text.strip():
                send_packet(self.socket, text)

    def close(self):
        self.stop_event.set()

        try:
            self.socket.close()
        except OSError:
            pass

        if self.receiver_thread:
            self.receiver_thread.join(timeout=1)


def main():
    client = Client(ADDR)

    try:
        client.connect()

        if not client.handshake():
            return

        client.start_receiver()
        client.input_loop()

    except KeyboardInterrupt:
        pass

    finally:
        client.close()


if __name__ == "__main__":
    main()

