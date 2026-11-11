import db

ENDPOINTS = ["ollama", "anthropic", "gemini", "web", "registry"]

def allowed(ep):
    c = db.conn()
    r = c.execute("SELECT allowed FROM network WHERE endpoint=?", (ep,)).fetchone()
    c.close()
    return bool(r and r["allowed"])

def set_allowed(ep, val):
    db.conn().execute("INSERT INTO network(endpoint,allowed) VALUES (?,?) ON CONFLICT(endpoint) DO UPDATE SET allowed=excluded.allowed",
                      (ep, int(val)))
    db.conn().commit()
    db.conn().close()

def all_status():
    c = db.conn()
    rows = c.execute("SELECT endpoint,allowed FROM network").fetchall()
    c.close()
    return {r["endpoint"]: bool(r["allowed"]) for r in rows}

def airgap():
    return db.get_setting("airgap", "0") == "1"

def set_airgap(v):
    db.set_setting("airgap", "1" if v else "0")
    if v:
        for ep in ["anthropic", "gemini", "web", "registry"]:
            set_allowed(ep, False)
