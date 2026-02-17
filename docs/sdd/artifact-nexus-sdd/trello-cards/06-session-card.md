# Card 06: Session Card Component

| Field | Value |
|-------|-------|
| **ID** | AN-06 |
| **Story Points** | 2 |
| **Depends On** | AN-04 (Static Layout) |
| **Sprint** | Phase 1 |

## User Story

> As a user, I want to see sessions as cards in the center pane so that I can quickly scan and select sessions.

## Context

- [ui-flow.md](../ui-flow.md) - Section 3 (Session Card Format)
- [requirements.md](../requirements.md) - Section 4.2 (Session Card Format)

## Instructions

### Step 1: Create SessionCard Widget

```python
# src/nexus/tui/session_card.py
from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message

class SessionCard(Widget):
    """Represents a session in the event stream."""
    
    CSS = """
    SessionCard {
        height: auto;
        min-height: 4;
        background: $surface;
        border: solid $primary;
        margin: 1 0;
        padding: 0 1;
    }
    
    SessionCard.selected {
        background: $primary-darken-2;
        border: solid $accent;
    }
    
    SessionCard:hover {
        background: $surface-darken-1;
    }
    
    SessionCard .card-header {
        color: $text-muted;
        padding: 0;
    }
    
    SessionCard .card-body {
        color: $text;
        padding: 0;
    }
    
    SessionCard .card-footer {
        color: $text-muted;
        padding: 0;
    }
    
    SessionCard .badge {
        background: $primary;
        color: $text;
        padding: 0 1;
        margin: 0 1;
    }
    
    SessionCard .badge-success {
        background: $success;
    }
    
    SessionCard .badge-failure {
        background: $error;
    }
    
    SessionCard .badge-interrupted {
        background: $warning;
    }
    """
    
    # Selection state
    selected = reactive(False)
    
    class Selected(Message):
        """Emitted when card is selected/deselected."""
        def __init__(self, session_id: int, selected: bool):
            self.session_id = session_id
            self.selected = selected
            super().__init__()
    
    def __init__(
        self,
        session_id: int,
        title: str,
        project_name: str,
        time_delta: str,
        status: str,
        agent_type: str,
        model: str,
        summary: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.title = title
        self.project_name = project_name
        self.time_delta = time_delta
        self.status = status
        self.agent_type = agent_type
        self.model = model
        self.summary = summary
    
    def compose(self):
        # Line 1: Header
        icon = self._get_status_icon()
        yield Static(
            f"{icon} {self.time_delta}  {self.project_name}",
            classes="card-header"
        )
        
        # Line 2: Body (summary)
        yield Static(self.summary, classes="card-body")
        
        # Line 3: Footer (badges)
        status_class = f"badge-{self.status}"
        yield Static(
            f"[{status_class}] {self.status} [/{status_class}]  "
            f"[{self.agent_type}]  "
            f"{self.model}",
            classes="card-footer"
        )
    
    def _get_status_icon(self) -> str:
        """Get status icon."""
        icons = {
            "success": "✅",
            "failure": "❌",
            "interrupted": "⏳"
        }
        return icons.get(self.status, "⏳")
    
    def watch_selected(self, selected: bool) -> None:
        """Update visual style when selection changes."""
        if selected:
            self.add_class("selected")
        else:
            self.remove_class("selected")
    
    def on_click(self) -> None:
        """Toggle selection on click."""
        self.selected = not self.selected
        self.post_message(self.Selected(self.session_id, self.selected))
    
    def on_key(self, event) -> None:
        """Handle space key for selection."""
        if event.key == " ":
            self.selected = not self.selected
            self.post_message(self.Selected(self.session_id, self.selected))
```

### Step 2: Create SessionStream Container

```python
# src/nexus/tui/session_stream.py
from textual.widgets import Static
from textual.containers import Vertical
from .session_card import SessionCard

class SessionStream(Vertical):
    """Container for session cards."""
    
    CSS = """
    SessionStream {
        height: 100%;
        overflow-y: auto;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cards: dict[int, SessionCard] = {}
    
    def add_session(self, session: dict) -> None:
        """Add a session card to the stream."""
        session_id = session["id"]
        
        if session_id in self.cards:
            return  # Already exists
        
        card = SessionCard(
            session_id=session_id,
            title=session.get("title", "Untitled"),
            project_name=session.get("project_name", "unknown"),
            time_delta=self._format_time_delta(session.get("start_time")),
            status=session.get("status", "interrupted"),
            agent_type=session.get("agent_type", "unknown"),
            model=session.get("model", "unknown"),
            summary=session.get("summary", ""),
            id=f"session-{session_id}"
        )
        
        self.mount(card)
        self.cards[session_id] = card
    
    def clear_sessions(self) -> None:
        """Remove all session cards."""
        for card in self.cards.values():
            card.remove()
        self.cards.clear()
    
    def load_sessions(self, sessions: list) -> None:
        """Load multiple sessions."""
        self.clear_sessions()
        for session in sessions:
            self.add_session(session)
    
    def _format_time_delta(self, start_time: str) -> str:
        """Format time delta from ISO timestamp."""
        from datetime import datetime
        
        if not start_time:
            return "Unknown"
        
        try:
            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            now = datetime.now(start.tzinfo)
            delta = now - start
            
            if delta.days > 7:
                return start.strftime("%Y-%m-%d")
            elif delta.days > 0:
                return f"{delta.days}d ago"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600}h ago"
            elif delta.seconds > 60:
                return f"{delta.seconds // 60}m ago"
            else:
                return "Just now"
        except:
            return "Unknown"
    
    def get_selected_sessions(self) -> list[int]:
        """Get IDs of selected sessions."""
        return [
            card.session_id
            for card in self.cards.values()
            if card.selected
        ]
```

## Acceptance Criteria

- [ ] SessionCard widget class
- [ ] selected reactive attribute
- [ ] 3-line format: header, body, footer
- [ ] Visual style for selected state (TCSS)
- [ ] Click handler for toggle
- [ ] Space key handler for toggle
- [ ] Icon by status: ✅/❌/⏳
- [ ] Badge rendering for agent/model
- [ ] SessionStream container
- [ ] Time delta formatting

## Next Steps

1. Update state.json: set card 06 to "completed"
2. Continue with Card 07 (Inspector Pane)
