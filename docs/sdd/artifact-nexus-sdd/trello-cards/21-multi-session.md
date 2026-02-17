# Card 21: Multi-Session Selection

| Field | Value |
|-------|-------|
| **ID** | AN-21 |
| **Story Points** | 1 |
| **Depends On** | AN-06 |
| **Sprint** | Phase 3 |

## User Story

> As a user, I want to select multiple sessions and ask questions across all of them so that I can get comparative analysis.

## Context

- [requirements.md](../requirements.md) - Section 3.4 (Multi-Session Selection)
- [ui-flow.md](../ui-flow.md) - Flow 3: Multi-Session Chat
- User requirement added during GAP-005 interview

## Instructions

### Step 1: Add Selection State to Session Card

```python
# src/nexus/tui/session_card.py
from textual.widget import Widget
from textual.reactive import reactive

class SessionCard(Widget):
    """Represents a session in the event stream."""
    
    # Selection state
    selected = reactive(False)
    
    def __init__(self, session_data: dict):
        super().__init__()
        self.session_data = session_data
        self.session_id = session_data["id"]
    
    def watch_selected(self, selected: bool) -> None:
        """Update visual style when selection changes."""
        if selected:
            self.add_class("selected")
        else:
            self.remove_class("selected")
    
    def on_click(self) -> None:
        """Toggle selection on click."""
        self.selected = not self.selected
```

### Step 2: Add Space Key Handler

```python
# src/nexus/tui/main_screen.py
from textual.screen import Screen

class MainScreen(Screen):
    """Main 3-pane TUI screen."""
    
    def on_key(self, event) -> None:
        if event.key == "space":
            self._toggle_session_selection()
    
    def _toggle_session_selection(self) -> None:
        """Toggle selection of focused session card."""
        focused = self.focus
        if hasattr(focused, "selected"):
            focused.selected = not focused.selected
```

### Step 3: Track Selected Sessions

```python
# src/nexus/tui/main_screen.py
from typing import Set

class MainScreen(Screen):
    """Main 3-pane TUI screen."""
    
    def __init__(self):
        super().__init__()
        self.selected_session_ids: Set[int] = set()
    
    def _toggle_session_selection(self) -> None:
        """Toggle selection and update tracking set."""
        focused = self.focus
        if hasattr(focused, "selected") and hasattr(focused, "session_id"):
            focused.selected = not focused.selected
            
            if focused.selected:
                self.selected_session_ids.add(focused.session_id)
            else:
                self.selected_session_ids.discard(focused.session_id)
        
        # Update status bar
        self._update_status_bar()
    
    def _update_status_bar(self) -> None:
        """Update status bar with selection count."""
        count = len(self.selected_session_ids)
        if count > 0:
            self.sub_title = f"{count} session(s) selected"
        else:
            self.sub_title = "Artifact Nexus"
    
    def get_selected_sessions(self) -> list:
        """Get list of selected session data."""
        # Query database for selected session IDs
        return self.app.db.get_sessions_by_ids(self.selected_session_ids)
```

### Step 4: Add CSS for Selection

```css
/* src/nexus/tui/main.tcss */

SessionCard {
    background: $surface;
    border: solid $primary;
}

SessionCard.selected {
    background: $primary-darken-2;
    border: solid $accent;
}

SessionCard:hover {
    background: $surface-darken-1;
}
```

### Step 5: Pass Selection to Inspector

```python
# src/nexus/tui/main_screen.py
def on_key(self, event) -> None:
    if event.key == "enter":
        self._open_inspector()

def _open_inspector(self) -> None:
    """Open inspector with selected or focused session."""
    if self.selected_session_ids:
        # Multi-session mode
        sessions = self.get_selected_sessions()
        self.push_screen(InspectorScreen(sessions, multi_session=True))
    else:
        # Single session mode
        focused = self.focus
        if hasattr(focused, "session_data"):
            self.push_screen(InspectorScreen([focused.session_data]))
```

### Step 6: Update Chat Tab for Multi-Session

```python
# src/nexus/tui/inspector.py
class ChatTab(Widget):
    """Chat tab with Cognitive Router."""
    
    def __init__(self, sessions: list, multi_session: bool = False):
        super().__init__()
        self.sessions = sessions
        self.multi_session = multi_session
        self.session_ids = [s["id"] for s in sessions]
    
    def compose(self) -> ComposeResult:
        if self.multi_session:
            yield Static(f"Chat with {len(self.sessions)} sessions")
        else:
            yield Static(f"Chat: {self.sessions[0]['title']}")
        
        yield Input(placeholder="Ask a question...")
        yield Static(id="chat-history")
```

## Acceptance Criteria

- [ ] Space key toggles session selection
- [ ] Selected sessions visually highlighted (different background/border)
- [ ] Status bar shows selection count
- [ ] Selection persists across navigation
- [ ] Enter opens Inspector with selected sessions
- [ ] Chat tab shows "Chat with N sessions" for multi-selection
- [ ] Cognitive Router receives all selected session IDs
- [ ] Clear selection with 'c' key

## Next Steps

After completing this card:
1. Update state.json: set card 21 to "completed"
2. Read next card: [22-audit-logging.md](./22-audit-logging.md)
3. Continue to final card
