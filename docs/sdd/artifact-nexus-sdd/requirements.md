# Artifact Nexus - Functional Requirements

> Status: COMPLETE | Last updated: February 17, 2026

---

## 1. Session Ingestion

### 1.1 Session Sources

- System MUST support 4 CLI agents: Codex, Qwen, Kimi, Gemini
- System MUST read session files from standard paths:
  - Codex: `~/.codex/sessions/2026/{MM}/{DD}/rollout-*.jsonl`
  - Qwen: `~/.qwen/projects/{project}/chats/{session-id}.jsonl`
  - Kimi: `~/.kimi/sessions/{session-id}/{turn-id}/context.jsonl`
  - Gemini: `~/.gemini/tmp/{project-hash}/chats/session-*.json`

### 1.2 Agent Fingerprinting

- System MUST detect agent type from JSON structure:
  - **Codex:** `session_meta`, `turn_context`, `event_msg` types
  - **Qwen:** `type: system/user/assistant`, `sessionId`
  - **Kimi:** `role: user/assistant/_checkpoint`
  - **Gemini:** JSON file format (not JSONL), `session-*.json` pattern
- System MUST use "unknown" as fallback for unrecognized formats

### 1.3 Watcher Service

- System MUST poll for new sessions every 30 seconds
- System MUST support manual addition via `nexus add <path>`
- System MUST NOT delete sessions (files are append-only)

---

## 2. Data Model

### 2.1 SQLite Schema

- System MUST have `sessions` table with columns:
  - `id` (INTEGER PK), `filepath` (TEXT), `project_name` (TEXT)
  - `project_root` (TEXT), `agent_type` (TEXT), `start_time` (DATETIME)
  - `end_time` (DATETIME), `status` (TEXT), `summary` (TEXT), `title` (TEXT)
  - `created_at` (DATETIME)
- System MUST have `cognitive_audit` table for AI chat history:
  - `id` (INTEGER PK), `session_ids` (TEXT), `user_query` (TEXT)
  - `final_model` (TEXT), `chain_log` (TEXT), `created_at` (DATETIME)

### 2.2 Session Summary

- System MUST generate summary in format:
  ```
  [ACTION] Brief description | Files: file1.py, file2.js | Status
  ```
- System MUST extract title from first user prompt (60 chars max)
- System MUST determine status: `success`, `failure`, `interrupted`

---

## 3. User Interface

### 3.1 Three-Pane Layout

- System MUST display 3-pane TUI:
  - **Left (20%):** Filters (time range, agent type, status, search)
  - **Center (45%):** Event stream with session cards
  - **Right (35%):** Inspector (Details, Artifacts, Chat tabs)

### 3.2 Session Card Format

- System MUST render each session as 3-line card:
  ```
  [Icon] [Time Delta] [Project Path]
  [White text] Summary of user intent
  [Badges] Status | Agent | Model
  ```

### 3.3 Keyboard Navigation

- System MUST support Vim-style navigation:
  - `j/k` — Scroll stream up/down
  - `Space` — Toggle selection (multi-session)
  - `Enter` — Open session in Inspector
  - `f` — Focus Filter Pane
  - `c` — Clear all selections
  - `/` — Trigger Search mode

### 3.4 Multi-Session Selection

- System MUST allow selecting multiple sessions (Space key)
- System MUST support asking questions across selected sessions in Chat

---

## 4. Filtering

### 4.1 Filter Types

- System MUST support filtering by:
  - **Time Range:** Last 24h, Last 3 Days, Last Week, Custom
  - **Agent Type:** Codex, Qwen, Kimi, Gemini (checkboxes)
  - **Status:** Success, Failed, Interrupted
  - **Fuzzy Search:** Project names + Session titles

### 4.2 Fuzzy Search

- System MUST use `rapidfuzz` library for fuzzy matching
- System MUST support partial matches (threshold: 60%+)

---

## 5. Cognitive Router

### 5.1 Fallback Chain

- System MUST support model fallback chain defined in `~/.nexus/chains.yaml`
- System MUST retry next model ONLY on:
  - Auth error (401, 403)
  - Rate limit (429)
  - Timeout
  - Network error
- System MUST NOT fallback if model responded (even if answer is bad)

### 5.2 Configuration

- System MUST load chains from `~/.nexus/chains.yaml`:
  ```yaml
  chains:
    default:
      - name: "fast_triage"
        provider: "ollama"
        model: "qwen2.5-coder:32b"
        timeout: 15s
      - name: "deep_analysis"
        provider: "google"
        model: "gemini-1.5-pro-latest"
  ```

### 5.3 Context Strategy

- System MUST load full session content if tokens < limit
- System MUST load "Heads & Tails" (first 2 + last 2 interactions) if tokens > limit

---

## 6. Non-Functional Requirements

### 6.1 Performance

- TUI launch: < 2 seconds
- Filter response: < 500ms
- Cognitive Router response: < 30s per model

### 6.2 Security

- System MUST NOT store API keys (use system credentials)
- System MUST NOT transmit logs without explicit user query

### 6.3 Localization

- System MUST support Russian and English UI
- System MUST read language preference from config

---

## 7. Out of Scope

- Token count display (user has subscription)
- Cost estimation (user has subscription)
- Session deletion (files are append-only)
- Real-time streaming (30s polling is sufficient)
- Claude support (not in user's workflow)
- Web UI (terminal-only)

---

## References

- PRD: `/home/pets/temp/jsonl_dashboard/docs/PRD.md`
- Interview Log: `/home/pets/temp/jsonl_dashboard/docs/raw_requirements/interview_log.md`
- Raw Requirements: `/home/pets/temp/jsonl_dashboard/docs/raw_requirements/raw_requiremenst.md`
