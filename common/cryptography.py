import secrets
import base64
import json
from common.config import DH_P, DH_G, FORMAT
from Crypto.Cipher import AES

def generate_public_key(priv):
    return pow(DH_G, priv, DH_P)

def generate_private_key():
    min_bits = 256
    min_val = 2 ** (min_bits - 1) # 2^255
    max_val = DH_P - 2
    while True:
        key = secrets.randbelow(max_val - min_val) + min_val
        if key >= min_val:
            return key

def generate_session_key(pub, priv):
    return pow(pub,priv,DH_P)

def encrypt(key, plaintext):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode(FORMAT))
    nonce = cipher.nonce
    message = {
        'ciphertext': base64.b64encode(ciphertext).decode(FORMAT),
        'tag': base64.b64encode(tag).decode(FORMAT),
        'nonce': base64.b64encode(nonce).decode(FORMAT)
    }
    return json.dumps(message)


def decrypt(key, message):
    data = json.loads(message)

    ciphertext = base64.b64decode(data['ciphertext'])
    tag = base64.b64decode(data['tag'])
    nonce = base64.b64decode(data['nonce'])

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode(FORMAT)
    except ValueError as mac_mismatch:
        print("MAC validation failed during decryption")

