import socket

PORT = 5555
SERVER = '127.0.0.1'
HEADER = 16
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
ADDR = (SERVER, PORT)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    message_len = len(message)
    send_len = str(message_len).encode(FORMAT)
    send_len += b' ' * (HEADER - len(send_len))
    client_socket.send(send_len)
    client_socket.send(message)

    print(client_socket.recv(1024).decode(FORMAT))

if __name__ == "__main__":
    send('Hello world!')
    input()
    send('Druga')
    input()
    send(DISCONNECT_MESSAGE)
