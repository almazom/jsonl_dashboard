# Artifact Nexus - Manual E2E Test Scenarios

> Status: COMPLETE | Last updated: February 17, 2026

---

## Test Environment Setup

```bash
# Prerequisites
- Python 3.10+
- Codex CLI installed (~/.codex/sessions with data)
- Qwen CLI installed (~/.qwen/projects with data)
- ~/.nexus/chains.yaml configured

# Install and run
cd /home/pets/temp/jsonl_dashboard
poetry install
poetry run nexus
```

---

## Scenario 1: First Launch

**Goal:** Verify TUI launches and displays sessions.

**Steps:**
1. Run `nexus` command
2. Wait for TUI to load

**Expected:**
- TUI loads in < 2 seconds
- 3-pane layout visible
- Center pane shows session cards from Codex and Qwen
- Each card shows: icon, time delta, project name, summary, badges

**Pass Criteria:**
- [ ] TUI renders without errors
- [ ] At least 3 session cards visible
- [ ] No "No sessions" message (if data exists)

---

## Scenario 2: Filter by Agent Type

**Goal:** Verify filtering by agent type works.

**Steps:**
1. Press `f` to focus Filter Pane
2. Uncheck "Codex" checkbox
3. Observe Center pane

**Expected:**
- Only Qwen, Kimi, Gemini sessions visible
- Filter applies in < 500ms

**Pass Criteria:**
- [ ] Codex sessions hidden
- [ ] Other agents visible
- [ ] Filter response immediate

---

## Scenario 3: Fuzzy Search

**Goal:** Verify fuzzy search finds sessions.

**Steps:**
1. Press `/` to trigger search
2. Type "auth"
3. Observe results

**Expected:**
- Sessions with "auth" in project name or title highlighted
- Partial matches included (rapidfuzz >= 60%)

**Pass Criteria:**
- [ ] Matching sessions highlighted
- [ ] Non-matching sessions hidden or dimmed
- [ ] Press `Esc` clears search

---

## Scenario 4: Navigate and Inspect

**Goal:** Verify session inspection works.

**Steps:**
1. Press `j/k` to navigate to a session
2. Press `Enter`

**Expected:**
- Inspector opens on right pane
- Tab 1 (Details) shows: start_time, end_time, model, cwd, status

**Pass Criteria:**
- [ ] Inspector opens
- [ ] Details tab populated
- [ ] Can switch tabs with 1/2/3 keys

---

## Scenario 5: Multi-Session Selection

**Goal:** Verify selecting multiple sessions works.

**Steps:**
1. Navigate to first session
2. Press `Space` (should show selection indicator)
3. Navigate to second session
4. Press `Space`
5. Navigate to third session
6. Press `Space`
7. Press `Enter` to open Inspector

**Expected:**
- All 3 sessions show selection indicator
- Inspector title shows "3 selected sessions"

**Pass Criteria:**
- [ ] Multiple sessions selectable
- [ ] Selection persists across navigation
- [ ] Inspector acknowledges multi-selection

---

## Scenario 6: Chat with Single Session

**Goal:** Verify Cognitive Router works for single session.

**Steps:**
1. Open Inspector for a session
2. Switch to Tab 3 (Chat) with `3` key
3. Type: "What files were modified?"
4. Press Enter

**Expected:**
- Question sent to Cognitive Router
- First model in chain queried
- Answer displayed in chat
- Model name shown

**Pass Criteria:**
- [ ] Question accepted
- [ ] Answer received in < 30s
- [ ] Model name displayed

---

## Scenario 7: Chat with Multiple Sessions

**Goal:** Verify Cognitive Router works across multiple sessions.

**Steps:**
1. Select 3 sessions with `Space`
2. Open Inspector
3. Switch to Tab 3 (Chat)
4. Type: "Compare the changes across these sessions"
5. Press Enter

**Expected:**
- Context loaded from all 3 sessions
- Answer references all sessions
- Fallback chain works if first model fails

**Pass Criteria:**
- [ ] Context includes all selected sessions
- [ ] Answer is coherent across sessions
- [ ] Fallback works (if configured)

---

## Scenario 8: Fallback Chain

**Goal:** Verify model fallback works on auth error.

**Setup:**
```yaml
# ~/.nexus/chains.yaml
chains:
  default:
    - name: "test_invalid"
      provider: "openai"
      api_key: "invalid_key_here"  # Will fail
      timeout: 5s
    - name: "test_fallback"
      provider: "ollama"
      model: "qwen2.5-coder:32b"
```

**Steps:**
1. Open Chat tab
2. Ask any question
3. Observe logs

**Expected:**
- First model fails with 401
- Second model queried automatically
- Answer from second model displayed
- chain_log shows: "test_invalid failed (401) → test_fallback success"

**Pass Criteria:**
- [ ] First model failure detected
- [ ] Second model tried automatically
- [ ] Answer received
- [ ] chain_log recorded

---

## Scenario 9: Watcher Service

**Goal:** Verify Watcher polls for new sessions.

**Steps:**
1. Start `nexus` in terminal 1
2. Run Codex CLI in terminal 2, create new session
3. Wait 30 seconds
4. Observe terminal 1

**Expected:**
- New session appears in Center pane within 30s
- No manual refresh needed

**Pass Criteria:**
- [ ] New session detected
- [ ] Appears within 30-60 seconds
- [ ] No errors in logs

---

## Scenario 10: Graceful Degradation

**Goal:** Verify app handles missing data gracefully.

**Setup:**
```bash
# Empty session directory
mkdir -p /tmp/empty_nexus
nexus --watch-path /tmp/empty_nexus
```

**Steps:**
1. Run nexus with empty watch path
2. Observe UI

**Expected:**
- Message: "No sessions. Run `nexus add <path>` or wait for Watcher"
- UI still functional (filters, settings accessible)

**Pass Criteria:**
- [ ] No crash on empty data
- [ ] Helpful message displayed
- [ ] UI remains responsive

---

## Scenario 11: Keyboard Navigation

**Goal:** Verify all keyboard shortcuts work.

**Steps:**
1. Press each key: `j`, `k`, `Space`, `Enter`, `f`, `c`, `/`, `1`, `2`, `3`, `q`

**Expected:**
- Each key triggers correct action
- No conflicts or missed inputs

**Pass Criteria:**
- [ ] All keys respond correctly
- [ ] No lag or missed inputs

---

## Scenario 12: Exit and Restart

**Goal:** Verify state persists across restarts.

**Steps:**
1. Press `q` to quit
2. Run `nexus` again

**Expected:**
- Same sessions visible
- SQLite registry persisted
- No data loss

**Pass Criteria:**
- [ ] Sessions persist
- [ ] No corruption
- [ ] Fast restart (< 2s)

---

## Sign-Off

| Scenario | Tester | Date | Status |
|----------|--------|------|--------|
| 1. First Launch | | | ☐ |
| 2. Filter by Agent | | | ☐ |
| 3. Fuzzy Search | | | ☐ |
| 4. Navigate/Inspect | | | ☐ |
| 5. Multi-Session Select | | | ☐ |
| 6. Chat (Single) | | | ☐ |
| 7. Chat (Multi) | | | ☐ |
| 8. Fallback Chain | | | ☐ |
| 9. Watcher Service | | | ☐ |
| 10. Graceful Degradation | | | ☐ |
| 11. Keyboard Nav | | | ☐ |
| 12. Exit/Restart | | | ☐ |

**All scenarios must pass before marking SDD as READY FOR IMPLEMENTATION.**
