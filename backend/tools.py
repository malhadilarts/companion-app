import json
import time
import urllib.request
import urllib.parse
import db

# Built-in tool implementations
def _tool_web_search(args):
    # offline-safe: returns a stub unless network.web allowed
    import network
    if not network.allowed("web"):
        return {"error": "web access disabled in network settings"}
    q = args.get("query", "")
    try:
        url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote(q) if False else None
    except Exception:
        pass
    return {"note": "web search not implemented in MVP; query was: " + q}

def _tool_read_file(args):
    path = args.get("path", "")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return {"content": f.read(8000)}
    except Exception as e:
        return {"error": str(e)}

def _tool_list_dir(args):
    import os
    path = args.get("path", ".")
    try:
        return {"entries": os.listdir(path)}
    except Exception as e:
        return {"error": str(e)}

def _tool_remember(args):
    import memory
    mid = memory.add(args.get("fact", ""), kind="fact", source="tool")
    return {"stored": mid}

def _tool_recall(args):
    import memory
    hits = memory.search(args.get("query", ""), k=5)
    return {"results": [h["content"] for h in hits]}

BUILTIN = {
    "web_search": {"fn": _tool_web_search, "description": "Search the web (requires network.web)",
                   "schema": {"query": "string"}},
    "read_file": {"fn": _tool_read_file, "description": "Read a local text file",
                   "schema": {"path": "string"}},
    "list_dir": {"fn": _tool_list_dir, "description": "List a directory",
                 "schema": {"path": "string"}},
    "remember": {"fn": _tool_remember, "description": "Store a fact in long-term memory",
                 "schema": {"fact": "string"}},
    "recall": {"fn": _tool_recall, "description": "Recall relevant memories",
               "schema": {"query": "string"}},
}

def register_builtin():
    c = db.conn()
    now = time.time()
    for name, info in BUILTIN.items():
        c.execute("INSERT OR IGNORE INTO tools(name,description,schema,created_at) VALUES (?,?,?,?)",
                  (name, info["description"], json.dumps(info["schema"]), now))
    c.commit()
    c.close()

def list_tools():
    c = db.conn()
    rows = c.execute("SELECT name,description,schema,enabled FROM tools").fetchall()
    c.close()
    return [dict(r) for r in rows]

def set_enabled(name, val):
    c = db.conn()
    c.execute("UPDATE tools SET enabled=? WHERE name=?", (int(val), name))
    c.commit()
    c.close()

def run_tool(name, args):
    info = BUILTIN.get(name)
    if not info:
        return {"error": "unknown tool"}
    c = db.conn()
    r = c.execute("SELECT enabled FROM tools WHERE name=?", (name,)).fetchone()
    c.close()
    if r and not r["enabled"]:
        return {"error": "tool disabled"}
    try:
        return info["fn"](args or {})
    except Exception as e:
        return {"error": str(e)}

register_builtin()
