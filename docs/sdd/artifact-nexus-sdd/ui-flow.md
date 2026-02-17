# Artifact Nexus - UI Flow

> Status: COMPLETE | Last updated: February 17, 2026

---

## 1. Main TUI Layout

```
┌─────────────────┬──────────────────────────┬─────────────────────┐
│   FILTERS       │      EVENT STREAM        │     INSPECTOR       │
│   (20%)         │        (45%)             │       (35%)         │
│                 │                          │                     │
│ Time Range      │ 🤖 2h ago  cdx_proxy_... │ Tab 1: Details      │
│ ☑ Codex         │ [FIX] Auth error in...   │ Tab 2: Artifacts    │
│ ☑ Qwen          │ ✅ Success | Codex       │ Tab 3: Chat         │
│ ☐ Kimi          │                          │                     │
│ ☐ Gemini        │ 🤖 5h ago  flow_fact...  │                     │
│                 │ [ADD] Unit tests for...  │                     │
│ Status:         │ ⏳ Interrupted | Qwen    │                     │
│ ☑ Success       │                          │                     │
│ ☐ Failed        │ 🤖 1d ago  translation   │                     │
│ ☐ Interrupted   │ [FIX] Encoding issue...  │                     │
│                 │ ✅ Success | Kimi        │                     │
│ Search: /       │                          │                     │
└─────────────────┴──────────────────────────┴─────────────────────┘
```

---

## 2. User Flows

### Flow 1: Watch (Browse Sessions)

```
1. User runs `nexus` command
   ↓
2. TUI launches, shows all sessions
   ↓
3. User presses 'j/k' to scroll
   ↓
4. User sees session cards with summary
   ↓
5. User presses 'f' to focus filters
   ↓
6. User toggles agent checkboxes
   ↓
7. Stream updates with filtered results
```

### Flow 2: Inspect (View Session Details)

```
1. User navigates to session with 'j/k'
   ↓
2. User presses 'Enter'
   ↓
3. Inspector opens with session details
   ↓
4. User sees:
   - Tab 1: Metadata (time, model, cwd, status)
   - Tab 2: Artifacts (files mentioned/created)
   - Tab 3: Chat (AI Q&A)
   ↓
5. User switches tabs with number keys
```

### Flow 3: Multi-Session Chat

```
1. User navigates to first session
   ↓
2. User presses 'Space' to select
   ↓
3. User navigates to second session
   ↓
4. User presses 'Space' to select
   ↓
5. User navigates to third session
   ↓
6. User presses 'Space' to select
   ↓
7. User presses 'Enter' to open Inspector
   ↓
8. User switches to Tab 3: Chat
   ↓
9. User types question about all 3 sessions
   ↓
10. Cognitive Router loads context from all selected sessions
   ↓
11. Router queries models with fallback chain
   ↓
12. Answer displayed in chat
```

### Flow 4: Fuzzy Search

```
1. User presses '/' key
   ↓
2. Search input focused
   ↓
3. User types partial text (e.g., "auth")
   ↓
4. System filters sessions by:
   - Project name (rapidfuzz >= 60%)
   - Session title (rapidfuzz >= 60%)
   ↓
5. Matching sessions highlighted
   ↓
6. User presses 'Enter' to confirm search
   ↓
7. User presses 'Esc' to clear search
```

---

## 3. Session Card States

| State | Icon | Badge Color |
|-------|------|-------------|
| Success | ✅ | Green |
| Failed | ❌ | Red |
| Interrupted | ⏳ | Yellow |

---

## 4. Keyboard Shortcuts Reference

| Key | Action |
|-----|--------|
| `j` | Scroll down |
| `k` | Scroll up |
| `Space` | Toggle session selection |
| `Enter` | Open Inspector |
| `f` | Focus Filter Pane |
| `c` | Clear selections/filters |
| `/` | Trigger Search |
| `Esc` | Clear search / Close Inspector |
| `1` | Switch to Tab 1 (Details) |
| `2` | Switch to Tab 2 (Artifacts) |
| `3` | Switch to Tab 3 (Chat) |
| `q` | Quit application |

---

## 5. Chat Interface

```
┌─────────────────────────────────────────┐
│  Chat with 3 selected sessions          │
├─────────────────────────────────────────┤
│  User: What files were modified?        │
│                                         │
│  Assistant: Based on the 3 sessions:    │
│  - Session 1: auth.py, test_auth.py     │
│  - Session 2: middleware.py             │
│  - Session 3: config.yaml               │
│                                         │
│  Model: Gemini 1.5 Pro (fallback used)  │
├─────────────────────────────────────────┤
│  > Type your question...          [Send]│
└─────────────────────────────────────────┘
```

---

## 6. Error States

| Error | Display |
|-------|---------|
| No sessions found | "No sessions. Run `nexus add <path>` or wait for Watcher" |
| Cognitive Router unavailable | "Chat unavailable. Check ~/.nexus/chains.yaml" |
| All models failed | "All models in chain failed. Last error: {error}" |
