import json
import urllib.request
import urllib.error
from config import OLLAMA_URL, DEFAULT_MODEL
import network
import vault

def stream_tokens(messages, model=None):
    model = model or DEFAULT_MODEL
    if not network.allowed("ollama"):
        raise RuntimeError("Ollama endpoint disabled in network settings")
    payload = {"model": model, "messages": messages, "stream": True}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        for line in resp:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            tok = obj.get("message", {}).get("content", "")
            if tok:
                yield tok
            if obj.get("done"):
                break

def chat_stream(messages, model=None, on_token=None):
    for tok in stream_tokens(messages, model=model):
        if on_token:
            on_token(tok)

def chat(messages, model=None):
    return "".join(stream_tokens(messages, model=model))

def list_models():
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=10) as r:
            j = json.loads(r.read())
            return [m["name"] for m in j.get("models", [])]
    except Exception:
        return []

def _anthropic_messages(messages):
    sys = None
    msgs = []
    for m in messages:
        if m["role"] == "system":
            sys = m["content"]
        else:
            msgs.append({"role": m["role"], "content": m["content"]})
    return sys, msgs

def anthropic_stream(messages, model="claude-sonnet-4-5"):
    if not network.allowed("anthropic"):
        raise RuntimeError("Anthropic disabled")
    key = vault.get_key("anthropic")
    if not key:
        raise RuntimeError("No Anthropic key in vault")
    sys, msgs = _anthropic_messages(messages)
    body = {"model": model, "max_tokens": 2048, "messages": msgs, "stream": True}
    if sys:
        body["system"] = sys
    data = json.dumps(body).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=data,
                                 headers={"Content-Type": "application/json",
                                          "x-api-key": key,
                                          "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=300) as r:
        for raw in r:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                obj = json.loads(payload)
            except Exception:
                continue
            if obj.get("type") == "content_block_delta":
                t = obj.get("delta", {}).get("text")
                if t:
                    yield t
            elif obj.get("type") == "message_stop":
                break

def anthropic_chat(messages, model="claude-sonnet-4-5"):
    return "".join(anthropic_stream(messages, model=model))

def gemini_stream(messages, model="gemini-2.0-flash"):
    if not network.allowed("gemini"):
        raise RuntimeError("Gemini disabled")
    key = vault.get_key("gemini")
    if not key:
        raise RuntimeError("No Gemini key in vault")
    contents = []
    for m in messages:
        if m["role"] == "system":
            continue
        contents.append({"role": "user" if m["role"] == "user" else "model",
                         "parts": [{"text": m["content"]}]})
    body = {"contents": contents}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={key}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        for raw in r:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                obj = json.loads(payload)
            except Exception:
                continue
            cands = obj.get("candidates", [])
            if cands:
                parts = cands[0].get("content", {}).get("parts", [])
                for p in parts:
                    t = p.get("text")
                    if t:
                        yield t

def gemini_chat(messages, model="gemini-2.0-flash"):
    return "".join(gemini_stream(messages, model=model))

def route_chat(messages, provider="ollama", model=None):
    if provider == "anthropic":
        return anthropic_chat(messages, model or "claude-sonnet-4-5")
    if provider == "gemini":
        return gemini_chat(messages, model or "gemini-2.0-flash")
    return chat(messages, model=model)
