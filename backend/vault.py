import base64
import hashlib
import json
import os
import secrets
from pathlib import Path

from config import MASTER_KEY_PATH, VAULT_PATH

def _master_key():
    if MASTER_KEY_PATH.exists():
        return MASTER_KEY_PATH.read_bytes()
    k = secrets.token_bytes(32)
    MASTER_KEY_PATH.write_bytes(k)
    try:
        os.chmod(MASTER_KEY_PATH, 0o600)
    except Exception:
        pass
    return k

def _derive(key_bytes, salt):
    return hashlib.pbkdf2_hmac("sha256", key_bytes, salt, 200000, dklen=32)

def _xor(data: bytes, key: bytes) -> bytes:
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key[i % len(key)])
    return bytes(out)

def _load_vault():
    if not VAULT_PATH.exists():
        return {}
    try:
        raw = VAULT_PATH.read_bytes()
        salt = raw[:16]
        blob = raw[16:]
        k = _derive(_master_key(), salt)
        dec = _xor(blob, k)
        return json.loads(dec.decode("utf-8"))
    except Exception:
        return {}

def _save_vault(d):
    salt = secrets.token_bytes(16)
    k = _derive(_master_key(), salt)
    blob = _xor(json.dumps(d).encode("utf-8"), k)
    VAULT_PATH.write_bytes(salt + blob)

def set_key(provider, api_key):
    d = _load_vault()
    d[provider] = api_key
    _save_vault(d)

def get_key(provider):
    return _load_vault().get(provider)

def delete_key(provider):
    d = _load_vault()
    d.pop(provider, None)
    _save_vault(d)

def list_keys():
    return list(_load_vault().keys())
