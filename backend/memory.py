import json
import time

import db

_model = None
_ST_AVAILABLE = None

def _st_available():
    global _ST_AVAILABLE
    if _ST_AVAILABLE is None:
        try:
            import sentence_transformers  # noqa
            _ST_AVAILABLE = True
        except Exception:
            _ST_AVAILABLE = False
    return _ST_AVAILABLE

def _embedder():
    global _model
    if _model is None and _st_available():
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed(text):
    if not _st_available():
        return None
    try:
        import numpy as np
        v = _embedder().encode(text, normalize_embeddings=True)
        return v.astype("float32").tobytes()
    except Exception:
        return None

def add(content, kind="fact", source=None, pinned=False):
    now = time.time()
    emb = embed(content)
    c = db.conn()
    c.execute(
        "INSERT INTO memory(kind,content,embedding,source,pinned,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
        (kind, content, emb, source, int(pinned), now, now),
    )
    c.commit()
    rid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.close()
    return rid

def update(mid, content):
    now = time.time()
    emb = embed(content)
    c = db.conn()
    c.execute("UPDATE memory SET content=?, embedding=?, updated_at=? WHERE id=?", (content, emb, now, mid))
    c.commit()
    c.close()

def delete(mid):
    c = db.conn()
    c.execute("DELETE FROM memory WHERE id=?", (mid,))
    c.commit()
    c.close()

def list_all(kind=None):
    c = db.conn()
    if kind:
        rows = c.execute("SELECT id,kind,content,source,pinned,created_at,updated_at FROM memory WHERE kind=? ORDER BY updated_at DESC", (kind,)).fetchall()
    else:
        rows = c.execute("SELECT id,kind,content,source,pinned,created_at,updated_at FROM memory ORDER BY updated_at DESC").fetchall()
    c.close()
    return [dict(r) for r in rows]

def search(query, k=6):
    rows = list_all()
    if not rows:
        return []
    # embedding similarity if available
    if not _st_available():
        scored = sorted(rows, key=lambda r: _keyword_score(query, r["content"]), reverse=True)
        return scored[:k]
    try:
        import numpy as np
        qv = _embedder().encode(query, normalize_embeddings=True).astype("float32")
        scored = []
        c = db.conn()
        for r in rows:
            row = c.execute("SELECT embedding FROM memory WHERE id=?", (r["id"],)).fetchone()
            emb = row["embedding"] if row else None
            if emb:
                v = np.frombuffer(emb, dtype="float32")
                score = float(np.dot(qv, v))
            else:
                score = _keyword_score(query, r["content"])
            scored.append((score, r))
        c.close()
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:k]]
    except Exception:
        scored = sorted(rows, key=lambda r: _keyword_score(query, r["content"]), reverse=True)
        return scored[:k]

def _keyword_score(q, text):
    qwords = set(q.lower().split())
    twords = set(text.lower().split())
    if not qwords:
        return 0.0
    return len(qwords & twords) / len(qwords)

def build_context(query, budget_chars=4000):
    hits = search(query, k=8)
    pinned = [m for m in list_all() if m["pinned"]]
    chosen = pinned + [h for h in hits if h not in pinned]
    out = []
    total = 0
    for m in chosen:
        line = f"- [{m['kind']}] {m['content']}"
        if total + len(line) > budget_chars:
            break
        out.append(line)
        total += len(line)
    return "\n".join(out)
