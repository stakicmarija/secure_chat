import socket
import threading

from common.config import ADDR, QUIT_COMMAND
from common.messages import ClientMessage, ServerMessage, build_hello
from common.protocol import recv_packet, send_packet


class Client:

    def __init__(self, addr):
        self.addr = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.stop_event = threading.Event()
        self.receiver_thread = None

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
        print("Username accepted. You can now send messages.")
        print(f"Use {QUIT_COMMAND} to disconnect.")
        return True

    def receive_loop(self):
        while not self.stop_event.is_set():
            try:
                message = recv_packet(self.socket)

                if message is None:
                    print("[SYSTEM] Connection to server was lost. Press Enter to exit.")
                    self.stop_event.set()
                    break

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

            if text.strip():
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