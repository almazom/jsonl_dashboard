# Artifact Nexus - Trello Board

> **Execution Order:** Linear (01 → 22)  
> **Total Cards:** 22  
> **Total SP:** 48

---

## Pipeline Visualization

```
Phase 1: Core Scaffolding (16 SP)
┌────┬────┬────┬────┬────┬────┬────┐
│ 01 │ 02 │ 03 │ 04 │ 05 │ 06 │ 07 │
│ 2  │ 3  │ 3  │ 3  │ 2  │ 2  │ 1  │
├────┼────┼────┼────┼────┼────┼────┤
│BOOT│ DB │ DB │TUI │FILT│CARD│INSP│
└────┴────┴────┴────┴────┴────┴────┘
              ↓
Phase 2: Ingestion & Stream (18 SP)
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ 08 │ 09 │ 10 │ 11 │ 12 │ 13 │ 14 │ 15 │
│ 3  │ 2  │ 2  │ 2  │ 3  │ 2  │ 2  │ 2  │
├────┼────┼────┼────┼────┼────┼────┼────┤
│CODX│QWEN│KIMI│GEMN│SCAN│WTCH│FILTR│FUZZ│
└────┴────┴────┴────┴────┴────┴────┴────┘
              ↓
Phase 3: Cognitive Engine (14 SP)
┌────┬────┬────┬────┬────┬────┬────┐
│ 16 │ 17 │ 18 │ 19 │ 20 │ 21 │ 22 │
│ 2  │ 3  │ 3  │ 2  │ 2  │ 1  │ 1  │
├────┼────┼────┼────┼────┼────┼────┤
│CNFG│ROUT│FALL│CHAT│CNTX│MULT│AUDT│
└────┴────┴────┴────┴────┴────┴────┘
```

---

## Card Index

### Phase 1: Core Scaffolding

| # | File | Title | SP | Status |
|---|------|-------|----|--------|
| 01 | [01-project-bootstrap.md](./01-project-bootstrap.md) | Project Bootstrap | 2 | ☐ Todo |
| 02 | [02-database-schema.md](./02-database-schema.md) | Database Schema Design | 3 | ☐ Todo |
| 03 | [03-database-manager.md](./03-database-manager.md) | DatabaseManager Class | 3 | ☐ Todo |
| 04 | [04-static-layout.md](./04-static-layout.md) | Static 3-Pane Layout | 3 | ☐ Todo |
| 05 | [05-filter-pane.md](./05-filter-pane.md) | Filter Pane Component | 2 | ☐ Todo |
| 06 | [06-session-card.md](./06-session-card.md) | Session Card Component | 2 | ☐ Todo |
| 07 | [07-inspector-pane.md](./07-inspector-pane.md) | Inspector Pane Shell | 1 | ☐ Todo |

### Phase 2: Ingestion & Stream

| # | File | Title | SP | Status |
|---|------|-------|----|--------|
| 08 | [08-codex-parser.md](./08-codex-parser.md) | Codex JSONL Parser | 3 | ☐ Todo |
| 09 | [09-qwen-parser.md](./09-qwen-parser.md) | Qwen JSONL Parser | 2 | ☐ Todo |
| 10 | [10-kimi-parser.md](./10-kimi-parser.md) | Kimi JSONL Parser | 2 | ☐ Todo |
| 11 | [11-gemini-parser.md](./11-gemini-parser.md) | Gemini JSON Parser | 2 | ☐ Todo |
| 12 | [12-session-scanner.md](./12-session-scanner.md) | SessionScanner | 3 | ☐ Todo |
| 13 | [13-watcher-service.md](./13-watcher-service.md) | Watcher Service (30s) | 2 | ☐ Todo |
| 14 | [14-filter-logic.md](./14-filter-logic.md) | Filter Logic (SQL) | 2 | ☐ Todo |
| 15 | [15-fuzzy-search.md](./15-fuzzy-search.md) | Fuzzy Search (rapidfuzz) | 2 | ☐ Todo |

### Phase 3: Cognitive Engine

| # | File | Title | SP | Status |
|---|------|-------|----|--------|
| 16 | [16-chains-config.md](./16-chains-config.md) | chains.yaml Parser | 2 | ☐ Todo |
| 17 | [17-cognitive-router.md](./17-cognitive-router.md) | CognitiveRouter Class | 3 | ☐ Todo |
| 18 | [18-fallback-chain.md](./18-fallback-chain.md) | Fallback Chain Logic | 3 | ☐ Todo |
| 19 | [19-chat-ui.md](./19-chat-ui.md) | Chat UI Component | 2 | ☐ Todo |
| 20 | [20-context-loader.md](./20-context-loader.md) | Context Loader | 2 | ☐ Todo |
| 21 | [21-multi-session.md](./21-multi-session.md) | Multi-Session Selection | 1 | ☐ Todo |
| 22 | [22-audit-logging.md](./22-audit-logging.md) | Audit Logging | 1 | ☐ Todo |

---

## Progress Tracking

| Phase | Cards | Done | SP Done | % Complete |
|-------|-------|------|---------|------------|
| Phase 1 | 7 | 0 | 0/16 | 0% |
| Phase 2 | 8 | 0 | 0/18 | 0% |
| Phase 3 | 7 | 0 | 0/14 | 0% |
| **TOTAL** | **22** | **0** | **0/48** | **0%** |

---

## Dependencies

```
01 → 02 → 03 → 04 → 05 → 06 → 07  (Phase 1: sequential)
                    ↓
08 → 09 → 10 → 11 → 12 → 13 → 14 → 15  (Phase 2: parsers parallel, rest sequential)
                              ↓
16 → 17 → 18 → 19 → 20 → 21 → 22  (Phase 3: sequential)
```

---

## Definition of Done (per card)

- [ ] Code implemented
- [ ] Type checking passes
- [ ] No lint errors
- [ ] Unit tests written (if applicable)
- [ ] state.json updated
- [ ] Git committed (auto-daemon or manual)

---

**Start with Card 01. Update state.json after each card.**
