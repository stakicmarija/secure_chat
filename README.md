# SecureChat  
## A Python-based end-to-end encrypted chat application using:
- TCP socket communication between clients via a central server
- Diffie-Hellman key exchange (RFC 3526, 2048-bit MODP Group 14) for session key establishment
- SHA-256 key derivation from DH shared secret
- AES-256-GCM authenticated encryption ensuring confidentiality and message integrity
- Real-time active user list with automatic updates on connect/disconnect
- Peer selection - choose who you want to chat with using /chat <username>

## Usage
Start the server:

```bash
python3 -m server.server

```

Start clients (in  separate terminals):

```bash
python3 -m client.client

```

## Commands

- `/chat <username>` Start an encrypted session with a user 
- `/quit` to disconnect from the server

## Protocol Overview

### Connection & Registration
1. Client connects to server via TCP
2. Client sends `HELLO:<username>` 
3. Server responds with `HELLO_OK` or an error
4. Server broadcasts updated user list to all clients

### Session Establishment (Diffie-Hellman)
1. Alice sends `/chat bob` — client sends `DH_INIT:bob:alice:<public_key>`
2. Server forwards message to Bob
3. Bob automatically responds with `DH_RESPONSE:alice:bob:<public_key>`
4. Server forwards response to Alice
5. Both parties independently compute the shared secret and derive an AES-256 key via SHA-256

### Encrypted Messaging
1. Sender encrypts plaintext using AES-256-GCM
2. Message is sent as `CHAT:<target>:<sender>:<json_payload>`
3. JSON payload contains `ciphertext`, `tag`, and `nonce` — all Base64 encoded
4. Server forwards payload to target without being able to read contents
5. Recipient decrypts and verifies message integrity using the tag

## Status
This project is actively being developed. Planned improvements...
