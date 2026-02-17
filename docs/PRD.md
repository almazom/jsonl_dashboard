# Product Requirements Document (PRD)

## Project: Artifact Nexus

**Version:** 1.1  
**Date:** February 17, 2026  
**Document Status:** Ready for Task Breakdown  
**Based on:** RPD v1.0 + Interview Clarifications

---

## 1. Executive Summary

**Artifact Nexus** is a terminal-based observability and cognitive analysis platform designed for developers managing distributed multi-agent systems (Gemini CLI, Codex, Qwen, Kimi).

Unlike traditional log viewers, Artifact Nexus provides a **Semantic Timeline** of agent activities and includes a **Cognitive Router**—an integrated AI engine that allows users to query logs using a fallback chain of Large Language Models (LLMs). The system transforms static JSON/JSONL artifacts into an interactive, queryable knowledge base.

### Key Value Proposition

- **Single view** across all AI agent sessions (Codex, Qwen, Kimi, Gemini)
- **Semantic search** instead of manual log browsing
- **AI-powered Q&A** over your session history with automatic fallback

---

## 2. System Architecture

### 2.1 High-Level Design

The system follows a **Model-View-Controller (MVC)** pattern adapted for a Terminal User Interface (TUI).

| Component | Role | Technology |
|-----------|------|------------|
| **The Registry (Model)** | SQLite database storing session metadata | `sqlite3` |
| **The Watcher (Controller)** | Background service scanning for new sessions | Polling (30s) |
| **The Nexus TUI (View)** | 3-pane interface for filtering and inspection | `Textual` |
| **The Cognitive Router (Logic)** | Async LLM engine with fallback chains | `litellm` |

### 2.2 Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| TUI Framework | `Textual` (CSS-driven terminal UI) |
| Database | `sqlite3` (Standard Library) |
| LLM Interface | `litellm` or direct API SDKs |
| Configuration | `PyYAML` |
| Fuzzy Search | `rapidfuzz` |

---

## 3. Supported Agents (Session Sources)

| Agent | Session Path | Format | Notes |
|-------|--------------|--------|-------|
| **Codex** | `~/.codex/sessions/2026/{MM}/{DD}/rollout-*.jsonl` | JSONL | Date-based folders |
| **Qwen** | `~/.qwen/projects/{project}/chats/{session-id}.jsonl` | JSONL | Project = escaped path |
| **Kimi** | `~/.kimi/sessions/{session-id}/{turn-id}/context.jsonl` | JSONL | Nested session/turn structure |
| **Gemini** | `~/.gemini/tmp/{project-hash}/chats/session-*.json` | JSON | Hash = SHA256 of path |

---

## 4. Functional Requirements

### FR-01: Session Ingestion & Fingerprinting

The system must identify and index agent sessions from raw files.

| ID | Requirement | Implementation Notes |
|----|-------------|---------------------|
| FR-01.1 | Support manual addition via CLI (`nexus add <path>`) | Single file or directory |
| FR-01.2 | Support background scanning of "Workspace" directories | Polling every 30 seconds |
| FR-01.3 | **Heuristic Fingerprinting**: detect agent type from JSON structure | See table below |

**Agent Detection Heuristics:**

| Agent | Detection Keys |
|-------|----------------|
| Codex | `session_meta`, `turn_context`, `event_msg` types |
| Qwen | `type: system/user/assistant`, `sessionId` |
| Kimi | `role: user/assistant/_checkpoint` |
| Gemini | JSON (not JSONL), `session-*.json` pattern |
| Generic | Default fallback if no specific keys found |

---

### FR-02: Session Grouping (Clustering)

Raw files must be grouped into logical "Sessions" to reduce noise.

| ID | Requirement | Implementation Notes |
|----|-------------|---------------------|
| FR-02.1 | **One JSONL/JSON file = One Session** | No time-based grouping |
| FR-02.2 | **Session Title**: First meaningful user prompt (60 chars) | Skip system instructions |
| FR-02.3 | **Project Root**: Use `cwd` from session metadata | `project_name` = last folder |

**UI Grouping:**
```
▼ cdx_proxy_cli_v2 (10 sessions)
  ├─ [Session 1] Fix auth bug in login.py
  ├─ [Session 2] Add unit tests for auth
  └─ [Session 3] Refactor middleware

▼ other_project (5 sessions)
  └─ ...
```

---

### FR-03: Session Summary (Semantic Understanding)

Each session must have a human-readable summary.

**Summary Format:**
```
[ACTION] Brief description | Files: file1.py, file2.js | Status | Tokens
```

**Example:**
```
[FIX] Auth error in auth.py | Files: auth.py, test_auth.py | Success | 20k
```

**Extraction Algorithm:**
1. Find first user prompt → extract verb (fix, add, create, remove)
2. Find mentioned files (`.py`, `.js`, `.ts`, etc.)
3. Determine status from last event (success/failure/interrupted)
4. Extract token count if available (optional—user has subscription)

---

### FR-04: Faceted Filtering

Users must be able to slice the timeline view.

| ID | Filter Type | Options |
|----|-------------|---------|
| FR-04.1 | Time Range | Last 24h, Last 3 Days, Last Week, Custom |
| FR-04.2 | Agent Type | Codex, Qwen, Kimi, Gemini (dynamic checkboxes) |
| FR-04.3 | Status | Success, Failed, Interrupted |
| FR-04.4 | Fuzzy Search | Project names + Session titles (rapidfuzz) |

---

### FR-05: The Cognitive Router (AI Chat)

The system must enable "Chat with Context" using a defined chain of models.

| ID | Requirement | Implementation Notes |
|----|-------------|---------------------|
| FR-05.1 | **Fallback Logic**: Retry next model on failure | Only on: auth error (401/403), rate limit (429), timeout, network error |
| FR-05.2 | **Configuration**: `~/.nexus/chains.yaml` | YAML format (see Appendix) |
| FR-05.3 | **No fallback on bad answers** | If model responds, do not fallback |

**Fallback Triggers:**
- ✅ Auth error (401, 403)
- ✅ Rate limit (429)
- ✅ Timeout
- ✅ Network error
- ❌ Empty response (model answered)
- ❌ "I don't know" (model answered)
- ❌ Wrong answer (model answered)

---

## 5. User Interface Specifications

### 5.1 Layout Strategy (Three-Pane View)

```
┌─────────────────┬──────────────────────────┬─────────────────────┐
│   Filters       │      Event Stream        │     Inspector       │
│   (20%)         │        (45%)             │       (35%)         │
│                 │                          │                     │
│ • Time Range    │ [Session Card 1]         │ Tab 1: Details      │
│ • Agent Type ☑  │ [Session Card 2]         │ Tab 2: Artifacts    │
│ • Status        │ [Session Card 3]         │ Tab 3: Chat         │
│ • Search (/)    │                          │                     │
└─────────────────┴──────────────────────────┴─────────────────────┘
```

### 5.2 Session Card Format (Center Pane)

Each card is 3 lines high:

```
[Icon] [Time Delta] [Project Path]
[White text] Summary of user intent
[Badges] Status | Agent | Model
```

**Example:**
```
🤖 2h ago  cdx_proxy_cli_v2
[FIX] Auth error in login.py - added retry logic
✅ Success | Codex | gpt-5.3-codex
```

### 5.3 Key Interaction Model (Vim-Style)

| Key | Action |
|-----|--------|
| `j` / `k` | Scroll stream up/down |
| `Space` | Toggle selection (batch analysis) |
| `Enter` | Open session in Inspector |
| `f` | Focus Filter Pane |
| `c` | Clear all selections |
| `/` | Trigger Search mode |

### 5.4 Inspector Tabs (Right Pane)

| Tab | Content |
|-----|---------|
| **Details** | Metadata: start/end time, model, cwd, status |
| **Artifacts** | Files mentioned/created in session |
| **Chat** | Interactive chat with Cognitive Router |

---

## 6. Data Schema

### 6.1 Database Schema (SQLite)

**Table: `sessions`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Unique ID |
| `filepath` | TEXT | Absolute path to JSON/JSONL file |
| `project_name` | TEXT | Last folder of `cwd` (e.g., `cdx_proxy_cli_v2`) |
| `project_root` | TEXT | Full `cwd` from session |
| `agent_type` | TEXT | `codex`, `qwen`, `kimi`, `gemini`, `unknown` |
| `start_time` | DATETIME | Timestamp of first event |
| `end_time` | DATETIME | Timestamp of last event |
| `status` | TEXT | `success`, `failure`, `interrupted` |
| `summary` | TEXT | Auto-generated summary string |
| `title` | TEXT | First user prompt (60 chars) |
| `created_at` | DATETIME | When ingested into registry |

**Table: `cognitive_audit`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Unique ID |
| `session_ids` | TEXT | Comma-separated session IDs |
| `user_query` | TEXT | Question asked by user |
| `final_model` | TEXT | Model that successfully answered |
| `chain_log` | TEXT | Fallback log (e.g., "Qwen failed → Gemini success") |
| `created_at` | DATETIME | When query was made |

---

## 7. Configuration Reference

### 7.1 chains.yaml Format

```yaml
# ~/.nexus/chains.yaml
chains:
  default:
    # Step 1: Fast & Cheap (Local)
    - name: "fast_triage"
      provider: "ollama"
      model: "qwen2.5-coder:32b"
      timeout: 15s
      context_limit: 32000

    # Step 2: High Context (Cloud)
    - name: "deep_analysis"
      provider: "google"
      model: "gemini-1.5-pro-latest"
      temperature: 0.2
      context_limit: 2000000
```

### 7.2 Workspace Configuration

```yaml
# ~/.nexus/config.yaml
watcher:
  polling_interval: 30  # seconds
  
workspaces:
  - ~/.codex/sessions
  - ~/.qwen/projects
  - ~/.kimi/sessions
  - ~/.gemini/tmp
```

---

## 8. Implementation Roadmap

### Phase 1: Core Scaffolding (Day 1-2)

**Objective:** Get the TUI running with dummy data.

| Task | Priority | Notes |
|------|----------|-------|
| Initialize Python project with `poetry` | P0 | Python 3.10+ |
| Add dependencies: `textual`, `sqlite3`, `rapidfuzz`, `pyyaml` | P0 | |
| Implement `DatabaseManager` class | P0 | SQLite schema |
| Build static 3-pane layout in Textual | P0 | CSS styling |

---

### Phase 2: Ingestion & Stream (Day 3-4)

**Objective:** Populate the Center Pane with real data.

| Task | Priority | Notes |
|------|----------|-------|
| Implement `LogParser` for Codex JSONL | P0 | See Appendix A |
| Implement `LogParser` for Qwen JSONL | P1 | Different structure |
| Implement `LogParser` for Kimi JSONL | P1 | Different structure |
| Implement `LogParser` for Gemini JSON | P2 | Not JSONL! |
| Implement `SessionScanner` | P0 | Crawl directories |
| Implement `Watcher` service (30s polling) | P1 | Background thread |
| Connect `FilterPane` to SQL queries | P0 | `SELECT * FROM sessions` |
| Implement fuzzy search with `rapidfuzz` | P1 | Project + title |

---

### Phase 3: The Cognitive Engine (Day 5-7)

**Objective:** Enable "Chat with Context".

| Task | Priority | Notes |
|------|----------|-------|
| Implement `CognitiveRouter` class | P0 | Async fallback chain |
| Create `chains.yaml` parser | P0 | Load model config |
| Build Chat UI in Inspector (Tab 3) | P0 | Interactive interface |
| Implement context loading | P1 | Full vs. Heads&Tails |
| Handle fallback triggers | P0 | Auth/timeout/429 only |

---

## 9. Out of Scope (Explicitly Excluded)

| Feature | Reason |
|---------|--------|
| Token count display | User has subscription |
| Cost estimation | User has subscription |
| Session deletion | Not supported by CLI agents |
| Real-time streaming | Polling (30s) is sufficient |
| Claude support | Not in user's workflow |

---

## 10. Appendix

### Appendix A: Session Data Extraction

**Codex JSONL:**
```python
# User prompt
if event['type'] == 'response_item' and event['payload'].get('role') == 'user':
    prompt = event['payload']['content'][0]['text']

# Agent response
if event['type'] == 'response_item' and event['payload'].get('role') == 'assistant':
    response = event['payload']['content'][0]['text']

# Status
if event['type'] == 'event_msg' and event['payload'].get('type') == 'task_completed':
    status = 'success'

# Tokens
if event['type'] == 'event_msg' and event['payload'].get('type') == 'token_count':
    tokens = event['payload']['info']['total_token_usage']['total_tokens']

# Model
if event['type'] == 'turn_context':
    model = event['payload']['model']

# cwd (project root)
if event['type'] == 'turn_context':
    cwd = event['payload']['cwd']
```

**Qwen JSONL:**
```python
# User message
if event['type'] == 'user':
    prompt = event['message']['parts'][0]['text']

# Assistant response
if event['type'] == 'assistant':
    response = event['message']['parts'][0]['text']

# cwd
cwd = event['cwd']

# Model
model = event['model']
```

**Kimi JSONL:**
```python
# User message
if event['role'] == 'user':
    prompt = event['content']

# Assistant response
if event['role'] == 'assistant':
    response = event['content']
```

**Gemini JSON:**
```python
# Structure differs - needs investigation
# File format: JSON (not JSONL)
```

---

## 11. PRD Readiness Assessment

### ✅ Ready for Task Breakdown

| Criterion | Status | Notes |
|-----------|--------|-------|
| Session paths identified | ✅ | Codex, Qwen, Kimi, Gemini |
| Data extraction logic | ✅ | Codex, Qwen, Kimi documented |
| Database schema | ✅ | Finalized |
| UI layout | ✅ | 3-pane design complete |
| Fallback logic | ✅ | Auth/timeout/429 only |
| Tech stack | ✅ | Python + Textual + SQLite |
| Out of scope | ✅ | Explicitly listed |

### ⚠️ Minor Gaps (Can Be Resolved During Implementation)

| Gap | Impact | Resolution |
|-----|--------|------------|
| Gemini JSON structure | Low | Reverse-engineer from sample files |
| Context compression algorithm | Low | Implement basic version, iterate |
| Exact summary format | Low | Refine based on user feedback |

---

**Recommendation:** **PROCEED** to task breakdown and implementation.

All critical requirements are defined. Minor gaps can be resolved during Phase 2 (Ingestion) when working with actual session files.
