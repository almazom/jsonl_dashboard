# Artifact Nexus - KICKOFF

> **Mission:** Build Artifact Nexus — терминальная платформа для observability AI-агентов с Cognitive Router.

**Status:** READY FOR IMPLEMENTATION  
**Cards:** 22 (48 SP total)  
**Phases:** 3 (Scaffolding → Ingestion → Cognitive)

---

## Quick Start

```bash
# 1. Read this file
cat docs/sdd/artifact-nexus-sdd/trello-cards/KICKOFF.md

# 2. Start with Card 01
cat docs/sdd/artifact-nexus-sdd/trello-cards/01-*.md

# 3. Execute cards in order (01 → 22)
```

---

## Execution Rules

1. **Linear order:** Complete cards 01 → 02 → ... → 22
2. **Max 4 SP per card:** If bigger, split it
3. **Each card independently testable:** See manual-e2e-test.md
4. **Update state.json after each card:** Mark completed
5. **No implementation before SDD approval:** Guardian Gate passed

---

## Phase Breakdown

### Phase 1: Core Scaffolding (Cards 01-07, 16 SP)

**Goal:** Get TUI running with dummy data.

| Card | Title | SP |
|------|-------|----|
| 01 | Project Bootstrap | 2 |
| 02 | Database Schema | 3 |
| 03 | DatabaseManager Class | 3 |
| 04 | Static 3-Pane Layout | 3 |
| 05 | Filter Pane Component | 2 |
| 06 | Session Card Component | 2 |
| 07 | Inspector Pane Shell | 1 |

**Exit Criteria:**
- TUI launches and shows 3-pane layout
- Dummy sessions visible in Center pane
- Filters clickable (no logic yet)
- Inspector opens (empty tabs)

---

### Phase 2: Ingestion & Stream (Cards 08-15, 18 SP)

**Goal:** Populate Center Pane with real data.

| Card | Title | SP |
|------|-------|----|
| 08 | Codex JSONL Parser | 3 |
| 09 | Qwen JSONL Parser | 2 |
| 10 | Kimi JSONL Parser | 2 |
| 11 | Gemini JSON Parser | 2 |
| 12 | SessionScanner | 3 |
| 13 | Watcher Service (30s polling) | 2 |
| 14 | Filter Logic (SQL queries) | 2 |
| 15 | Fuzzy Search (rapidfuzz) | 2 |

**Exit Criteria:**
- Real sessions from all 4 CLI agents visible
- Watcher polls every 30s
- Filters work (time, agent, status)
- Fuzzy search finds sessions

---

### Phase 3: Cognitive Engine (Cards 16-22, 14 SP)

**Goal:** Enable "Chat with Context".

| Card | Title | SP |
|------|-------|----|
| 16 | chains.yaml Parser | 2 |
| 17 | CognitiveRouter Class | 3 |
| 18 | Fallback Chain Logic | 3 |
| 19 | Chat UI Component | 2 |
| 20 | Context Loader (full vs heads&tails) | 2 |
| 21 | Multi-Session Selection | 1 |
| 22 | cognitive_audit Table + Logging | 1 |

**Exit Criteria:**
- Chat tab functional
- Questions sent to Cognitive Router
- Fallback chain works (auth/timeout/429)
- Multi-session chat works
- Audit log recorded

---

## Complexity Assessment

| Factor | Points |
|--------|--------|
| New database table (2 tables) | +4 |
| External integration (4 CLI + 3 LLM) | +28 |
| New UI component (3-pane TUI) | +6 |
| Real-time features (Watcher) | +3 |
| **TOTAL** | **41 points** |

**Score 41 > 30** → Split into phases (22 cards, 48 SP).

---

## Key Files

| File | Purpose |
|------|---------|
| `docs/sdd/artifact-nexus-sdd/requirements.md` | Functional requirements |
| `docs/sdd/artifact-nexus-sdd/ui-flow.md` | UI specifications |
| `docs/sdd/artifact-nexus-sdd/manual-e2e-test.md` | Test scenarios |
| `~/.nexus/config.yaml` | App configuration |
| `~/.nexus/chains.yaml` | Cognitive Router chains |
| `~/.nexus/nexus.db` | SQLite registry |

---

## Testing Strategy

1. **Unit tests:** pytest for parsers, DatabaseManager, CognitiveRouter
2. **Integration tests:** Watcher + Scanner end-to-end
3. **E2E tests:** manual-e2e-test.md scenarios
4. **Dry-run:** `nexus --no-watch` for deterministic testing

---

## Next Steps

1. Read Card 01: Project Bootstrap
2. Execute cards in order
3. Update state.json after each card
4. Run E2E tests after each phase

**Start now:** `cat docs/sdd/artifact-nexus-sdd/trello-cards/01-project-bootstrap.md`
