import threading
import time
import json
import db
import memory
import llm

_stop = threading.Event()
_thread = None

def _run_task(task):
    try:
        if task == "dream":
            # consolidate recent conversations into memory insights
            c = db.conn()
            rows = c.execute("SELECT role,content FROM conversations ORDER BY created_at DESC LIMIT 40").fetchall()
            c.close()
            text = "\n".join(f"{r['role']}: {r['content']}" for r in rows)
            if not text.strip():
                return
            prompt = [
                {"role": "system", "content": "You are a memory consolidation engine. Extract 3-5 durable facts about the user from the conversation. Output one fact per line, no numbering."},
                {"role": "user", "content": text},
            ]
            out = llm.route_chat(prompt)
            for line in out.splitlines():
                line = line.strip().lstrip("-*").strip()
                if line:
                    memory.add(line, kind="insight", source="dream")
        elif task == "reflect":
            mems = memory.list_all()[:10]
            ctx = "\n".join(m["content"] for m in mems)
            prompt = [
                {"role": "system", "content": "Reflect on the user's memory and write one short observation about patterns or needs. One sentence."},
                {"role": "user", "content": ctx or "no memory yet"},
            ]
            out = llm.route_chat(prompt)
            if out.strip():
                memory.add(out.strip(), kind="insight", source="reflect")
    except Exception as e:
        print("task error:", e)

def _loop():
    while not _stop.is_set():
        now = time.time()
        c = db.conn()
        rows = c.execute("SELECT id,task,run_at,repeat_seconds FROM scheduled WHERE enabled=1").fetchall()
        c.close()
        for r in rows:
            if r["run_at"] <= now:
                _run_task(r["task"])
                c = db.conn()
                if r["repeat_seconds"] and r["repeat_seconds"] > 0:
                    c.execute("UPDATE scheduled SET run_at=?, last_run=? WHERE id=?",
                              (now + r["repeat_seconds"], now, r["id"]))
                else:
                    c.execute("UPDATE scheduled SET enabled=0, last_run=? WHERE id=?", (now, r["id"]))
                c.commit()
                c.close()
        time.sleep(5)

def start():
    global _thread
    if _thread and _thread.is_alive():
        return
    _stop.clear()
    _thread = threading.Thread(target=_loop, daemon=True)
    _thread.start()

def stop():
    _stop.set()

def schedule(name, task, run_at, repeat=0):
    c = db.conn()
    c.execute("INSERT INTO scheduled(name,task,run_at,repeat_seconds) VALUES (?,?,?,?)",
              (name, task, run_at, repeat))
    c.commit()
    c.close()

def list_scheduled():
    c = db.conn()
    rows = c.execute("SELECT id,name,task,run_at,repeat_seconds,enabled,last_run FROM scheduled").fetchall()
    c.close()
    return [dict(r) for r in rows]
