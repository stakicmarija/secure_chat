import socket
import threading

from common.config import ADDR
from common.messages import ClientMessage, ServerMessage, parse_hello,\
    build_server_user_list, DiffieHellmanMessage, parse_dh_target
from common.protocol import recv_packet, send_packet


class Server:
    def __init__(self, addr):
        self.addr = addr
        self.host = addr[0]

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(addr)

        self.clients = {}       # username : socket
        self.sockets = {}       # socket : username
        self.clients_lock = threading.Lock()

    def broadcast_user_list(self):
        with self.clients_lock:
            clients = ' '.join(self.clients.keys())

        message = build_server_user_list(clients)

        for sock in self.sockets:
            try:
                send_packet(sock, message)
            except Exception:
                pass

    def forward_dh(self, message, target):
        with self.clients_lock:
            sock = self.clients.get(target)
        if sock:
            send_packet(sock, message)

    def remove_client(self, client_socket):
        with self.clients_lock:
            username = self.sockets.pop(client_socket, None)
            if username:
                self.clients.pop(username, None)

        try:
            client_socket.close()
        except OSError:
            pass
        finally:
            self.broadcast_user_list()

    def register_client(self, client_socket, address):
        hello = recv_packet(client_socket)
        username = parse_hello(hello)

        if username is None:
            send_packet(client_socket, ServerMessage.HELLO_ERR_INVALID_HELLO.value)
            return None

        if (not username) or (" " in username):
            send_packet(client_socket, ServerMessage.HELLO_ERR_INVALID_USERNAME.value)
            return None

        with self.clients_lock:
            if username in self.clients:
                taken = True
            else:
                self.clients[username] = client_socket
                self.sockets[client_socket] = username
                taken = False

        if taken:
            send_packet(client_socket, ServerMessage.HELLO_ERR_USERNAME_TAKEN.value)
            return None

        send_packet(client_socket, ServerMessage.HELLO_OK.value)
        self.broadcast_user_list()
        print(f"{address} registered as {username}")

        return username

    def handle_client(self, client_socket, address):
        print(f"New connection: {address} connected")

        try:
            username = self.register_client(client_socket, address)

            if username is None:
                client_socket.close()
                return

            while True:
                message = recv_packet(client_socket)
                if message is None or message == ClientMessage.DISCONNECT.value:
                    break

                if message.startswith(DiffieHellmanMessage.DH_INIT.value) \
                        or message.startswith(DiffieHellmanMessage.DH_RESPONSE.value):
                    target = parse_dh_target(message)
                    self.forward_dh(message, target)
                else:
                    print(f"{address} ({username}): {message}")

        except Exception as exc:
            print(f"[SERVER] Client thread error for {address}: {exc}")

        finally:
            self.remove_client(client_socket)
            print(f"Connection closed: {address}")

    def start(self):
        self.server_socket.listen()
        print(f"Server is listening on {self.host}...")

        try:
            while True:
                client_socket, address = self.server_socket.accept()

                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                )

                thread.start()
                print(f"Active connections: {threading.active_count() - 1}")

        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")

        finally:
            self.server_socket.close()


def main():
    server = Server(ADDR)
    print("Server is starting...")
    server.start()


if __name__ == "__main__":
    main()

