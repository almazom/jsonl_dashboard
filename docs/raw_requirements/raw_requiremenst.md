I cannot directly create a Google Doc file in your Drive, but I have compiled the **complete, professional text for the Requirements Package Document (RPD)** below.

You can **copy and paste** the content below directly into a Google Doc or a Markdown file (`RPD_Artifact_Nexus.md`) to share with your development team. It is structured to industry standards for software specifications.

---

# Requirements Package Document (RPD)

## Project: Artifact Nexus

**Version:** 1.0
**Date:** February 17, 2026
**Document Status:** Approved for Development

---

## 1. Executive Summary

**Artifact Nexus** is a terminal-based observability and cognitive analysis platform designed for developers managing distributed multi-agent systems (e.g., Gemini CLI, Codex, Qwen, Claude Code).

Unlike traditional log viewers, Artifact Nexus provides a **Semantic Timeline** of agent activities and includes a **Cognitive Router**—an integrated AI engine that allows users to query logs using a fallback chain of Large Language Models (LLMs). The system transforms static JSON/JSONL artifacts into an interactive, queryable knowledge base.

---

## 2. System Architecture

### 2.1 High-Level Design

The system follows a **Model-View-Controller (MVC)** pattern adapted for a Terminal User Interface (TUI).

* **The Registry (Model):** A SQLite database storing metadata of agent sessions. It acts as an index, pointing to raw JSONL files on disk without duplicating heavy content.
* **The Watcher (Controller):** A background service that scans directories or registered paths to ingest new session artifacts, apply heuristic tagging, and update the Registry.
* **The Nexus TUI (View):** A 3-pane interface built with the Python `Textual` library, providing filtering, stream visualization, and deep inspection.
* **The Cognitive Router (Logic):** An asynchronous engine managing LLM API calls with automatic fallback strategies (e.g., local model  cloud model) and context window management.

### 2.2 Tech Stack

* **Language:** Python 3.10+
* **TUI Framework:** `Textual` (CSS-driven terminal UI)
* **Database:** `sqlite3` (Standard Library)
* **LLM Interface:** `litellm` (for unified API calls) or direct API SDKs.
* **Configuration:** `PyYAML`

---

## 3. Functional Requirements (FR)

### FR-01: Session Ingestion & "Fingerprinting"

The system must identify and index agent sessions from raw files.

* **FR-01.1:** Support manual addition of files via CLI command (`nexus add <path>`).
* **FR-01.2:** Support background scanning of defined "Workspace" directories.
* **FR-01.3:** **Heuristic Fingerprinting**: automatically detect the agent type based on JSON structure.
* *Codex:* Presence of keys `top_p`, `temperature`, or file extension `.codex`.
* *Gemini:* Presence of `safety_ratings`, `candidates`, `finish_reason`.
* *Claude:* Presence of `stop_reason`, `anthropic_version`.
* *Generic:* Default fallback if no specific keys are found.



### FR-02: Session Grouping (Clustering)

Raw files must be grouped into logical "Sessions" to reduce noise.

* **FR-02.1:** Group files if they share the same **Project Root** AND created within a **15-minute sliding window**.
* **FR-02.2:** Generate a **Session Title** using the first 60 characters of the first user prompt found in the group.

### FR-03: Faceted Filtering

Users must be able to slice the timeline view.

* **FR-03.1:** Filter by **Time Range** (Last 24h, Last 3 Days, Last Week, Custom).
* **FR-03.2:** Filter by **Agent Type** (Dynamic checkboxes based on available data).
* **FR-03.3:** Filter by **Status** (Success, Failed, Stalled).
* **FR-03.4:** Support fuzzy text search across Project Names and Session Titles.

### FR-04: The Cognitive Router (AI Chat)

The system must enable "Chat with Context" using a defined chain of models.

* **FR-04.1:** **Fallback Logic:** If the primary model fails (API error, timeout, or low confidence), automatically retry with the next model in the chain.
* **FR-04.2:** **Configuration:** Chains must be defined in `~/.nexus/chains.yaml`.
* *Example:* `Qwen-72B (Local)`  `Gemini 1.5 Pro`  `Claude 3.5 Sonnet`.


* **FR-04.3:** **Context Strategy:**
* If total tokens < Limit: Load full JSONL content.
* If total tokens > Limit: Load "Heads & Tails" (first 2 interactions + last 2 interactions + error logs).



---

## 4. User Interface Specifications (UI/UX)

### 4.1 Layout Strategy (The "Three-Pane" View)

The TUI must adhere to a strict flexible grid layout.

* **Left Pane (Filters & Navigation):** [Width: 20%]
* Contains Radio Buttons for Time.
* Contains Checkboxes for Agent Types.
* Supports mouse click and keyboard navigation.


* **Center Pane (The Event Stream):** [Width: 45%]
* A scrollable `ListView`.
* Items are rendered as **Cards** (3 lines high):
1. *Header:* [Icon] [Time Delta] [Project Path]
2. *Body:* [White text] Summary of user intent.
3. *Footer:* [Badges] Status, File Count, Model Name.




* **Right Pane (The Inspector):** [Width: 35%]
* **Tab 1: Details:** Raw metadata, token usage, cost.
* **Tab 2: Artifacts:** List of files generated in that session.
* **Tab 3: Chat:** Interactive chat interface with the Cognitive Router.



### 4.2 Key Interaction Model (Vim-Style)

* `j` / `k`: Scroll Stream up/down.
* `Space`: Toggle selection of the focused session (for batch analysis).
* `Enter`: Open the focused session in the Inspector.
* `f`: Focus the Filter Pane.
* `c`: Clear all selections.
* `/`: Trigger "Search" mode.

---

## 5. Data Dictionary & Schema

### 5.1 Database Schema (`sqlite3`)

**Table: `sessions**`
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER PK | Unique ID |
| `filepath` | TEXT | Absolute path to the .json/.jsonl file |
| `project_root`| TEXT | Derived root folder of the project |
| `agent_type` | TEXT | 'codex', 'gemini', 'claude', 'unknown' |
| `start_time` | DATETIME | Timestamp of the first log entry |
| `end_time` | DATETIME | Timestamp of the last log entry |
| `status` | TEXT | 'success', 'failure', 'interrupted' |
| `summary` | TEXT | Cached summary string (auto-generated) |
| `token_est` | INTEGER | Estimated token count of the file |

**Table: `cognitive_audit**`
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER PK | Unique ID |
| `session_ids` | TEXT | Comma-separated IDs of analyzed sessions |
| `user_query` | TEXT | The question asked by the user |
| `final_model` | TEXT | The model that successfully answered |
| `chain_log` | TEXT | Log of fallbacks (e.g., "Qwen failed -> Gemini success") |

---

## 6. Implementation Roadmap

### Phase 1: Core Scaffolding (Day 1-2)

* **Objective:** Get the TUI running with dummy data.
* **Tasks:**
1. Initialize Python project with `textual` and `poetry`.
2. Implement `DatabaseManager` class (SQLite).
3. Build the static 3-pane layout in Textual.



### Phase 2: Ingestion & Stream (Day 3-4)

* **Objective:** Populate the Center Pane with real data.
* **Tasks:**
1. Implement `LogParser` with regex heuristics for generic JSONL.
2. Implement `SessionScanner` to crawl directories.
3. Connect `FilterPane` logic to SQL queries (`SELECT * FROM sessions WHERE...`).



### Phase 3: The Cognitive Engine (Day 5-7)

* **Objective:** Enable "Chat with Context".
* **Tasks:**
1. Implement `CognitiveRouter` class.
2. Create `~/.nexus/chains.yaml` parser.
3. Build the "Chat" UI in the Right Pane.
4. Implement the "Context Compression" logic for large files.



---

## 7. Configuration Reference (`chains.yaml`)

```yaml
# Default definition for the Cognitive Router
chains:
  default:
    # Step 1: Fast & Cheap (Local or Small API)
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
      trigger_condition: "on_failure_or_uncertainty"

