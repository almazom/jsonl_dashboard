# Agent Protocol - State Update Patterns

> **Purpose:** Machine-readable progress tracking for Artifact Nexus SDD

---

## state.json Schema

```json
{
  "feature": "artifact-nexus",
  "version": "1.0",
  "generated": "2026-02-17T00:00:00Z",
  "status": "in_progress",
  "phases": {
    "phase_1": {
      "name": "Core Scaffolding",
      "cards": 7,
      "done": 0,
      "sp_total": 16,
      "sp_done": 0
    },
    "phase_2": {
      "name": "Ingestion & Stream",
      "cards": 8,
      "done": 0,
      "sp_total": 18,
      "sp_done": 0
    },
    "phase_3": {
      "name": "Cognitive Engine",
      "cards": 7,
      "done": 0,
      "sp_total": 14,
      "sp_done": 0
    }
  },
  "cards": [
    {
      "id": "AN-01",
      "title": "Project Bootstrap",
      "sp": 2,
      "phase": 1,
      "status": "todo",
      "depends_on": [],
      "started_at": null,
      "completed_at": null
    }
    // ... cards 02-22
  ]
}
```

---

## Update Pattern

After completing each card:

1. **Update card status:**
   ```json
   "cards[NN]": {
     "status": "completed",
     "completed_at": "2026-02-17T15:30:00Z"
   }
   ```

2. **Update phase progress:**
   ```json
   "phases": {
     "phase_1": {
       "done": 1,
       "sp_done": 2
     }
   }
   ```

3. **Recalculate totals:**
   - Sum `done` cards per phase
   - Sum `sp_done` per phase
   - Update overall `% complete`

---

## Status Values

| Value | Meaning |
|-------|---------|
| `todo` | Not started |
| `in_progress` | Currently working |
| `completed` | Done, tested, committed |
| `blocked` | Waiting on dependency |

---

## Validation

```bash
# Validate state.json syntax
jq . docs/sdd/artifact-nexus-sdd/trello-cards/state.json

# Check progress
jq '.phases.phase_1.done' docs/sdd/artifact-nexus-sdd/trello-cards/state.json
```

---

## progress.md Sync

After updating state.json, also update progress.md:

```markdown
## Current Progress

- **Phase 1:** 1/7 cards (2/16 SP) - 12.5%
- **Phase 2:** 0/8 cards (0/18 SP) - 0%
- **Phase 3:** 0/7 cards (0/14 SP) - 0%
- **TOTAL:** 1/22 cards (2/48 SP) - 4.2%
```

---

**Rule:** Always update state.json BEFORE starting next card.
