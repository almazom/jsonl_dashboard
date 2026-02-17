# Artifact Nexus - SDD Requirements

> Status: ✅ 100% COMPLETE - READY FOR IMPLEMENTATION | All 22 cards generated | All gaps filled | Generated: February 18, 2026

## Overview

This folder contains Spec-Driven Development (SDD) documentation for the **Artifact Nexus** feature.

**Artifact Nexus** — терминальная платформа для разработчиков, работающих с несколькими AI-агентами (Codex, Qwen, Kimi, Gemini). Даёт единую временную шкалу всех сессий + AI-поиск через Cognitive Router с fallback chain.

## Documents

| File | Description | Status |
|------|-------------|--------|
| [requirements.md](./requirements.md) | Functional requirements | ✅ COMPLETE |
| [ui-flow.md](./ui-flow.md) | User interaction flow | ✅ COMPLETE |
| [gaps.md](./gaps.md) | Interview questions & answers | ✅ COMPLETE |
| [manual-e2e-test.md](./manual-e2e-test.md) | E2E test scenarios | ✅ COMPLETE |
| [trello-cards/](./trello-cards/) | Executable Trello cards | ✅ COMPLETE |

## Pipeline Summary

```
Session Files → Watcher → Parser → Registry → TUI → Cognitive Router
    ↓            ↓         ↓        ↓        ↓        ↓
 JSON/JSONL   30s poll  Extract  SQLite  3-pane  Fallback chain
```

## Quick Reference

| Aspect | Decision |
|--------|----------|
| **Channel** | Terminal (TUI via Textual) |
| **Detection** | Heuristic fingerprinting по JSON структуре |
| **Required Fields** | filepath, project_name, agent_type, status, summary |
| **Execution** | Python 3.10+ CLI application |
| **Delivery** | 3-pane TUI + AI chat interface |
| **Config** | `~/.nexus/config.yaml`, `~/.nexus/chains.yaml` |

## Session Sources

| Agent | Path | Format |
|-------|------|--------|
| Codex | `~/.codex/sessions/2026/{MM}/{DD}/` | JSONL |
| Qwen | `~/.qwen/projects/{project}/chats/` | JSONL |
| Kimi | `~/.kimi/sessions/{session}/{turn}/` | JSONL |
| Gemini | `~/.gemini/tmp/{hash}/chats/` | JSON |

## Development Notes

- [ ] Dry-run: Watcher polling можно отключить через `--no-watch`
- [ ] Python 3.10+ required (Textual dependency)
- [ ] Poetry для package management
- [ ] rapidfuzz для fuzzy search
- [ ] litellm для unified LLM API

## Implementation

See [trello-cards/BOARD.md](./trello-cards/BOARD.md) for:
- **22 cards** (48 SP total)
- Linear execution order: 01 → 22
- Machine-friendly instructions
- Max 4 SP per card

## Phases

| Phase | Cards | SP | Description |
|-------|-------|----|-------------|
| Phase 1 | 01-07 | 16 SP | Core Scaffolding (TUI + DB) |
| Phase 2 | 08-15 | 18 SP | Ingestion & Stream |
| Phase 3 | 16-22 | 14 SP | Cognitive Engine |

---

## Guardian Gate

**SDD Package готова к реализации.**

Для начала implementation:
```bash
# 1. Прочитать KICKOFF.md
cat docs/sdd/artifact-nexus-sdd/trello-cards/KICKOFF.md

# 2. Начать с Card 01
cat docs/sdd/artifact-nexus-sdd/trello-cards/01-*.md
```
