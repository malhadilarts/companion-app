import time
import db
import memory

def ingest(name, text):
    # chunk into ~800 char pieces
    chunks = []
    cur = ""
    for para in text.split("\n"):
        if len(cur) + len(para) > 800:
            if cur.strip():
                chunks.append(cur.strip())
            cur = para + "\n"
        else:
            cur += para + "\n"
    if cur.strip():
        chunks.append(cur.strip())
    doc_id = None
    c = db.conn()
    c.execute("INSERT INTO documents(name,content,chunks,created_at) VALUES (?,?,?,?)",
              (name, text, len(chunks), time.time()))
    doc_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.commit()
    c.close()
    for ch in chunks:
        memory.add(ch, kind="document", source=name)
    return {"id": doc_id, "chunks": len(chunks)}

def search(query, k=5):
    return memory.search(query, k=k)
