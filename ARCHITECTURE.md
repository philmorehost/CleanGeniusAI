# CleanGenius AI Architecture

CleanGenius AI utilizes a decoupled hybrid architecture combining an Electron desktop shell with a Python Flask backend process.

```
┌────────────────────────────────────────────────────────┐
│                   Electron Frontend                    │
│   (Frameless Window, Renderer Pages, Preload Bridge)   │
└───────────────────────────┬────────────────────────────┘
                            │ IPC / HTTP REST (Port 5000)
┌───────────────────────────▼────────────────────────────┐
│                    Python Backend                      │
│   (Flask Server, Scanner Engine, AI Providers, DB)     │
└────────────────────────────────────────────────────────┘
```

## System Components

1. **Electron Main Process (`src/main/index.js`)**:
   - Manages frameless window creation and titlebar IPC listeners.
   - Spawns the background Python process (`src/backend/main.py`).

2. **Electron Preload Bridge (`src/preload.js`)**:
   - Exposes safe `window.electronAPI` channels to renderer pages without node integration.

3. **Python Flask API Server (`src/backend/main.py`)**:
   - Exposes REST endpoints for scanning (`/api/scan/*`), cleanup (`/api/cleanup/*`), AI analysis (`/api/ai/*`), and reports (`/api/reports/*`).

4. **Disk Scanner & Duplicate Engine (`src/backend/scanner/`)**:
   - Multi-threaded disk traversal with pattern categorization (`node_modules`, `temp_files`, `browser_cache`, etc.).
   - Hash-based duplicate detection (size filter -> SHA-256 digest).

5. **AI Provider Abstraction (`src/backend/ai/`)**:
   - Abstract base class with implementations for DeepSeek, OpenAI, Claude, Gemini, and Ollama.
   - Includes graceful fallback logic and prompt token compressor.

6. **Database (`src/backend/database/models.py`)**:
   - SQLite database storing scan sessions, scanned files, cleanup history, and API usage stats.
