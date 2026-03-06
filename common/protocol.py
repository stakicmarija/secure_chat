from common.config import FORMAT, HEADER

def recv_exact(socket, size):
    data = b""
    while len(data) < size:
        chunk = socket.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def recv_packet(socket):
    header = recv_exact(socket, HEADER)
    if not header:
        return None

    payload_len_str = header.decode(FORMAT).strip()
    if not payload_len_str:
        return None

    payload_len = int(payload_len_str)
    payload = recv_exact(socket, payload_len)
    if payload is None:
        return None

    return payload.decode(FORMAT)


def send_packet(sock, msg):
    payload = msg.encode(FORMAT)
    payload_len = str(len(payload)).encode(FORMAT)
    header = payload_len + b" " * (HEADER - len(payload_len))
    sock.sendall(header)
    sock.sendall(payload)
