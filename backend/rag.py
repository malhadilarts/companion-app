import time
import db
import memory

def ingest(name, text):
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
    c = db.conn()
    c.execute("INSERT INTO documents(name,content,chunks,created_at) VALUES (?,?,?,?)",
              (name, text, len(chunks), time.time()))
    doc_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.commit()
    c.close()
    src = f"doc:{doc_id}"
    for ch in chunks:
        memory.add(ch, kind="document", source=src)
    return {"id": doc_id, "chunks": len(chunks)}

def search(query, k=5):
    return memory.search(query, k=k)

def delete_doc(doc_id):
    c = db.conn()
    c.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    c.execute("DELETE FROM memory WHERE source=?", (f"doc:{doc_id}",))
    c.commit()
    c.close()
