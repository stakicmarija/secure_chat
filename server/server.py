import socket
import threading

PORT = 5555
SERVER = '127.0.0.1'
#SERVER = socket.gethostbyname(socket.gethostname()) #isto mi vrati localhost
ADDR = (SERVER, PORT)
HEADER = 16
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)

def handle_client(client_socket, address):
    print(f"New connection: {address} connected")

    connected = True
    while connected:
        message_len = client_socket.recv(16).decode(FORMAT)
        if message_len:
            message_len = int(message_len)
            message = client_socket.recv(message_len).decode(FORMAT)
            if(message == DISCONNECT_MESSAGE):
                connected = False
            print(f"{address}: {message}")

            client_socket.send("Message received".encode(FORMAT))

    client_socket.close()


def server_start():
    server_socket.listen()
    print(f"Server is listening on {SERVER}...")
    while True:
        client_socket, address = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.start()
        print(f"Active connections: {threading.activeCount() - 1}")

if __name__ == "__main__":
    print("Server is starting...")
    server_start()
