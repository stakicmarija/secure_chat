import secrets
from common.config import DH_P, DH_G

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