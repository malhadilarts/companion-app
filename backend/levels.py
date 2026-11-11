import db

LEVEL_INFO = {
 "S1": ("Remembering", "Basic chat + short-term memory."),
 "S2": ("Perceptive", "Long-term memory of facts about you."),
 "S3": ("Connecting", "Network toggles + external providers (Claude/Gemini)."),
 "S4": ("Prepared", "Tool use with approval gate."),
 "S5": ("Living", "Scheduled tasks & reminders."),
 "S6": ("Understanding", "Memory editor + insight summaries."),
 "S7": ("Considerate", "Guardian: prompt-injection defense + safety modes."),
 "S8": ("Insightful", "Multi-model orchestration + self-reflection."),
 "S9": ("Wise", "Autonomous planning with human-in-the-loop."),
 "S10": ("Thinking", "Full agent: tools + memory + identity."),
 "B1": ("Dreaming", "Nightly consolidation of the day's conversations."),
 "B2": ("Echo", "Voice I/O (STT/TTS)."),
 "B3": ("Mirror", "Personality/character editor, multiple personas."),
 "B4": ("Forge", "Create custom tools/skills (MCP-style)."),
 "B5": ("Sanctuary", "Fully air-gapped mode, zero network."),
 "B6": ("Twin", "Encrypted sync between devices."),
 "B7": ("Oracle", "RAG over your own documents."),
 "B8": ("Guardian Angel", "Anomaly detection on memory changes."),
}

# Unlock requirements (level -> list of prerequisite levels)
REQUIRES = {
 "S1": [],
 "S2": ["S1"],
 "S3": ["S1","S2"],
 "S4": ["S1","S2","S3"],
 "S5": ["S4"],
 "S6": ["S2"],
 "S7": ["S4"],
 "S8": ["S4","S6","S7"],
 "S9": ["S8"],
 "S10": ["S9"],
 "B1": ["S6"],
 "B2": ["S3"],
 "B3": ["S2"],
 "B4": ["S4"],
 "B5": ["S3"],
 "B6": ["S1"],
 "B7": ["S4"],
 "B8": ["S7"],
}

def can_unlock(level):
    return all(db.is_unlocked(r) for r in REQUIRES.get(level, []))

def unlock(level):
    if not can_unlock(level):
        return False
    db.unlock_level(level)
    return True

def status():
    out = []
    for lvl, (name, desc) in LEVEL_INFO.items():
        out.append({
            "level": lvl, "name": name, "description": desc,
            "unlocked": db.is_unlocked(lvl),
            "can_unlock": can_unlock(lvl),
        })
    return out
