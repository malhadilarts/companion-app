import base64
import hashlib
import json
import secrets
import time
from pathlib import Path

from config import IDENTITY_PATH
import db

def _gen_keypair():
    # Use a simple Ed25519-like placeholder via secrets (no nacl). We store a random id + hmac secret.
    priv = secrets.token_hex(32)
    pub = hashlib.sha256(priv.encode()).hexdigest()
    return pub, priv

def create(name):
    pub, priv = _gen_keypair()
    c = db.conn()
    c.execute(
        "INSERT OR REPLACE INTO identity(id,name,pubkey,privkey,created_at,registered) VALUES (1,?,?,?,?,0)",
        (name, pub, priv, time.time()),
    )
    c.commit()
    c.close()
    return {"name": name, "pubkey": pub, "created_at": time.time()}

def get():
    c = db.conn()
    r = c.execute("SELECT name,pubkey,created_at,registered,reg_code FROM identity WHERE id=1").fetchone()
    c.close()
    if not r:
        return None
    return dict(r)

def register(code):
    c = db.conn()
    c.execute("UPDATE identity SET registered=1, reg_code=? WHERE id=1", (code,))
    c.commit()
    c.close()

def sign(message):
    """Local-only HMAC signature (NOT publicly verifiable - no asymmetric crypto available).
    Returns HMAC-SHA256(privkey, message). For public verification you'd need Ed25519/RSA
    (requires the 'cryptography' package, not installed)."""
    c = db.conn()
    r = c.execute("SELECT privkey FROM identity WHERE id=1").fetchone()
    c.close()
    if not r:
        return None
    import hmac
    return hmac.new(r["privkey"].encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()

def verify(message, signature):
    """Local verification only."""
    expected = sign(message)
    if expected is None:
        return False
    import hmac
    return hmac.compare_digest(expected, signature)
