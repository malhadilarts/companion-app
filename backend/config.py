import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "companion.db"
VAULT_PATH = DATA_DIR / "vault.bin"
IDENTITY_PATH = DATA_DIR / "identity.json"
MASTER_KEY_PATH = DATA_DIR / ".master"   # local obfuscation key (not a real secret store)
BACKUPS_DIR = DATA_DIR / "backups"
BACKUPS_DIR.mkdir(exist_ok=True)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("COMPANION_MODEL", "iamherebefore/qwen2.5-coder-3b-instruct-abliterated:latest")
EMBED_MODEL = "all-MiniLM-L6-v2"

DEVICE = "cpu"
PORT = 7870
HOST = "127.0.0.1"
VERSION = "0.1.0"
APP_NAME = "Companion"
