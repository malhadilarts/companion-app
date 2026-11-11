# Companion — Local-First AI Companion

[![CI](https://github.com/malhadilarts/companion-app/actions/workflows/ci.yml/badge.svg)](https://github.com/malhadilarts/companion-app/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)

> Own your AI. Local LLM + persistent memory + privacy vault + network toggles + level progression.
> Inspired by the "own your AI" idea, implemented from scratch.

A browser/desktop-ready companion app inspired by the "own your AI" idea:
local LLM + persistent memory + privacy vault + network toggles + level progression.

## Demo

```
┌─────────────────────────────────────────────┐
│  Companion  v0.1.0 · S2 Perceptive          │
├─────────────────────────────────────────────┤
│  Chat  │  Memory  │  Vault  │  Network ...  │
├─────────────────────────────────────────────┤
│  You: I like local AI and coffee.           │
│  AIB: Noted. I'll remember that.            │
│                                             │
│  Memory panel:                              │
│   #1 [fact] User likes local AI and coffee. │
│   #2 [insight] User prefers local-first.    │
└─────────────────────────────────────────────┘
```

## Feature matrix

| Area | Status |
|---|---|
| Streaming chat (Ollama/Anthropic/Gemini) | ✅ |
| Persistent memory + semantic search | ✅ |
| Editable memory panel | ✅ |
| Vault (API keys, local) | ✅ |
| Network allow-list + air-gap | ✅ |
| Guardian (prompt-injection scan) | ✅ |
| Tool registry + approval | ✅ |
| Document ingestion + RAG (Oracle) | ✅ |
| Scheduler + Dreaming consolidation | ✅ |
| Level unlock system (18 levels) | ✅ |
| Voice I/O (Echo) | 🔜 |
| Device sync (Twin) | 🔜 |
| Desktop installer (Tauri) | 🔜 |

## Run (browser mode)
```
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 7870
```
Open http://127.0.0.1:7870

## Levels
S1 Remembering → S2 Perceptive → S3 Connecting → S4 Prepared → S5 Living →
S6 Understanding → S7 Considerate → S8 Insightful → S9 Wise → S10 Thinking
Bonus: B1 Dreaming, B2 Echo, B3 Mirror, B4 Forge, B5 Sanctuary, B6 Twin, B7 Oracle, B8 Guardian Angel

## Features
- Chat via Ollama (or Anthropic/Gemini with your own key)
- Editable memory panel (facts/episodes/insights/documents)
- Vault for API keys (local obfuscation)
- Network allow-list + air-gap mode
- Guardian: prompt-injection scanner + external-content wrapping
- Tool registry with approval gate
- Document ingestion + retrieval (Oracle)
- Scheduler (dreaming/consolidation)
- Backup/restore

## Desktop packaging
Wrap the FastAPI backend + frontend in Tauri or Electron. The backend is a
standard ASGI app; spawn it as a sidecar process on app start.

## Legal note
This is an original implementation of a *concept*. It does not copy any third-party
code, branding, or trademarks. If you commercialize, get a freedom-to-operate
review regarding third-party patent filings.
