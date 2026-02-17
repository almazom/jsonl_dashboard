# Artifact Nexus - Parallel Implementation Plan

**Strategy:** Option B - Parallel Worktrees with Merge  
**Agents:** Codex, Qwen, Kimi (3 parallel implementations)  
**SSOT:** `ssot_kanban.yaml` (shared progress tracking)  
**Value:** Continuity, Non-Stop Execution  

---

## 📋 Overview

```
main/
├── ssot_kanban.yaml              ← Shared state (single source)
├── docs/sdd/artifact-nexus-sdd/  ← Shared SDD (read-only for agents)
├── worktrees/
│   ├── codex-impl/               ← Codex implementation
│   ├── qwen-impl/                ← Qwen implementation
│   └── kimi-impl/                ← Kimi implementation
└── merged/                       ← Final merged result (after all complete)
```

---

## 🎯 Phase 0: Setup (One-Time)

### Step 1: Initialize Git Repository

```bash
cd /home/pets/temp/jsonl_dashboard

# Initialize git
git init
git config user.name "Your Name"
git config user.email "your@email.com"

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
*.egg-info/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Project
*.log
.nexus/
*.db
EOF

# Initial commit - SDD Package
git add .
git commit -m "docs: complete SDD package with 22 Trello cards"

# Create worktrees
git worktree add worktrees/codex-impl -b codex-impl
git worktree add worktrees/qwen-impl -b qwen-impl
git worktree add worktrees/kimi-impl -b kimi-impl
```

### Step 2: Copy SSOT to Each Worktree

```bash
# Each worktree gets its own SSOT copy for tracking
cp ssot_kanban.yaml worktrees/codex-impl/ssot_kanban.yaml
cp ssot_kanban.yaml worktrees/qwen-impl/ssot_kanban.yaml
cp ssot_kanban.yaml worktrees/kimi-impl/ssot_kanban.yaml
```

### Step 3: Update SSOT for Multi-Agent Tracking

```yaml
# Add to ssot_kanban.yaml:

implementations:
  codex:
    branch: codex-impl
    path: worktrees/codex-impl
    status: not_started
    cards_completed: []
    current_card: null
    
  qwen:
    branch: qwen-impl
    path: worktrees/qwen-impl
    status: not_started
    cards_completed: []
    current_card: null
    
  kimi:
    branch: kimi-impl
    path: worktrees/kimi-impl
    status: not_started
    cards_completed: []
    current_card: null

merge_strategy:
  pick_best_from: true
  review_required: true
  conflict_resolution: manual
```

---

## 🚀 Phase 1: Parallel Implementation (All 3 Agents)

### Card Assignment Strategy

**All 3 agents implement ALL 22 cards independently**

| Card | Codex | Qwen | Kimi |
|------|-------|------|------|
| 01 | ✅ | ✅ | ✅ |
| 02 | ✅ | ✅ | ✅ |
| ... | ✅ | ✅ | ✅ |
| 22 | ✅ | ✅ | ✅ |

### Execution Rules (Per Agent)

```
For each agent (Codex, Qwen, Kimi):

1. Read ssot_kanban.yaml
2. Find next card with state=backlog
3. Update state: backlog → in_progress
4. Implement card (code + tests)
5. Update state: in_progress → done
6. Commit with message: "feat: Card XX - <name>"
7. Repeat for next card
```

### Card Order (Sequential Per Agent)

```
Phase 1.1: Core Scaffolding (Cards 01-07)
Phase 1.2: Ingestion Layer (Cards 08-15)
Phase 1.3: Cognitive Engine (Cards 16-22)
```

---

## 📊 Phase 2: Progress Tracking

### SSOT Update Pattern (Per Agent)

```yaml
# After Codex completes Card 01:
implementations:
  codex:
    status: in_progress
    cards_completed: [01]
    current_card: 02
    
  qwen:
    status: in_progress
    cards_completed: [01, 02]
    current_card: 03
    
  kimi:
    status: in_progress
    cards_completed: [01, 02, 03, 04]
    current_card: 05
```

### Progress Commands

```bash
# Check all implementations status
python scripts/check_progress.py

# Output:
# Codex: 7/22 cards (32%)
# Qwen:  5/22 cards (23%)
# Kimi:  9/22 cards (41%)
```

---

## 🔀 Phase 3: Merge Strategy

### When All 3 Complete (100%)

```bash
# Create merged branch
git checkout -b merged-impl

# Create src directory
mkdir -p src/nexus

# For each card, pick best implementation:
# - Codex: Clean code, good tests
# - Qwen:  Fast implementation
# - Kimi:  Security-focused, edge cases

# Example merge for Card 01:
cp worktrees/codex-impl/src/nexus/cli.py src/nexus/cli.py        # Codex wins
cp worktrees/qwen-impl/src/nexus/config.py src/nexus/config.py   # Qwen wins
cp worktrees/kimi-impl/src/nexus/logger.py src/nexus/logger.py   # Kimi wins
```

### Merge Decision Matrix

| Component | Pick From | Reason |
|-----------|-----------|--------|
| CLI Entry | Codex | Cleanest argparse |
| Database | Kimi | Best error handling |
| Parsers | Qwen | Fastest implementation |
| TUI | Codex | Best Textual patterns |
| Router | Kimi | Best circuit breaker |
| Tests | All 3 | Combine all test cases |

---

## 📝 Commit Message Convention

### Per-Agent Commits

```
feat: Card 01 - Project Bootstrap (codex)
feat: Card 01 - Project Bootstrap (qwen)
feat: Card 01 - Project Bootstrap (kimi)

feat: Card 02 - Database Schema (codex)
feat: Card 02 - Database Schema (qwen)
feat: Card 02 - Database Schema (kimi)
```

### Merge Commit

```
merge: Combine best implementations from all agents

Codex contributions:
- CLI entry point
- TUI components
- Unit test structure

Qwen contributions:
- Parser implementations
- Session scanner
- Filter logic

Kimi contributions:
- Database error handling
- Circuit breaker pattern
- Security hardening

All 22 cards implemented and tested.
```

---

## ⚠️ Conflict Resolution

### SSOT Conflicts

```yaml
# If multiple agents update same SSOT:
# Rule: Last write wins + merge manually

# Run merge script:
python scripts/merge_ssot.py \
  --codex worktrees/codex-impl/ssot_kanban.yaml \
  --qwen worktrees/qwen-impl/ssot_kanban.yaml \
  --kimi worktrees/kimi-impl/ssot_kanban.yaml \
  --output ssot_kanban.yaml
```

### Code Conflicts (During Merge)

```bash
# Use git mergetool
git mergetool

# Or manual resolution:
# 1. Compare all 3 implementations
# 2. Pick best parts
# 3. Document decision in merge commit
```

---

## 🎯 Success Criteria

### Per-Agent DoD (Definition of Done)

- [ ] All 22 cards implemented
- [ ] All unit tests pass
- [ ] No linting errors
- [ ] SSOT updated to 100%
- [ ] Git history clean (one commit per card)

### Merge DoD

- [ ] All components from best agent selected
- [ ] No merge conflicts unresolved
- [ ] All tests pass in merged version
- [ ] Documentation updated
- [ ] Ready for production

---

## 📅 Timeline Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| Setup (Phase 0) | 30 min | Git + worktrees |
| Implementation (Phase 1) | 3-5 days | Parallel (longest agent) |
| Merge (Phase 3) | 1 day | Pick best, resolve conflicts |
| **Total** | **4-6 days** | Single implementation would be 5-7 days |

---

## 🛠️ Scripts Needed

### check_progress.py

```python
#!/usr/bin/env python3
"""Check progress across all implementations."""
import yaml
from pathlib import Path

def check_progress():
    agents = ['codex', 'qwen', 'kimi']
    
    for agent in agents:
        path = Path(f'worktrees/{agent}-impl/ssot_kanban.yaml')
        if path.exists():
            with open(path) as f:
                data = yaml.safe_load(f)
            
            completed = len(data['implementations'][agent]['cards_completed'])
            print(f"{agent.capitalize()}: {completed}/22 cards ({completed*100//22}%)")

if __name__ == '__main__':
    check_progress()
```

### merge_ssot.py

```python
#!/usr/bin/env python3
"""Merge SSOT files from all agents."""
import yaml
import argparse

def merge_ssot(codex_path, qwen_path, kimi_path, output_path):
    # Load all SSOTs
    # Merge cards_completed from all
    # Write merged output
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--codex', required=True)
    parser.add_argument('--qwen', required=True)
    parser.add_argument('--kimi', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    merge_ssot(args.codex, args.qwen, args.kimi, args.output)
```

---

## 🚦 Next Steps

1. **Confirm this plan** - Reply "yes" to proceed
2. **Execute Phase 0** - Setup git + worktrees
3. **Start Phase 1** - All 3 agents begin Card 01
4. **Track progress** - SSOT updates after each card
5. **Execute Phase 3** - Merge when all complete

---

**Ready to start non-stop implementation?**

Reply "yes" and I'll:
1. Initialize git repository
2. Create worktrees for all 3 agents
3. Update SSOT for multi-agent tracking
4. Start Codex on Card 01
5. Start Qwen on Card 01
6. Start Kimi on Card 01

**All agents work in parallel, non-stop, until all 22 cards complete.**
