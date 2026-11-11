# Companion — Local-First AI Companion (re-engineered concept)

A browser/desktop-ready companion app inspired by the "own your AI" idea:
local LLM + persistent memory + privacy vault + network toggles + level progression.

## Run (browser mode)
```
cd companion-app/backend
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
