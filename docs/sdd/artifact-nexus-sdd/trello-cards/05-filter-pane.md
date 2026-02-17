# Card 05: Filter Pane Component

| Field | Value |
|-------|-------|
| **ID** | AN-05 |
| **Story Points** | 2 |
| **Depends On** | AN-04 (Static Layout) |
| **Sprint** | Phase 1 |

## User Story

> As a user, I want filter controls in the left pane so that I can narrow down sessions by time, agent type, and status.

## Context

- [ui-flow.md](../ui-flow.md) - Section 2 (User Flows)
- [requirements.md](../requirements.md) - Section 4.1 (Filter Types)

## Instructions

### Step 1: Create FilterPane Widget

```python
# src/nexus/tui/filter_pane.py
from textual.widget import Widget
from textual.widgets import Static, RadioButton, CheckBox, Input
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.message import Message

class FilterPane(Widget):
    """Left pane filter controls."""
    
    CSS = """
    FilterPane {
        height: 100%;
        padding: 1;
    }
    
    FilterPane .section-title {
        text-style: bold;
        margin: 1 0;
    }
    
    FilterPane .filter-section {
        margin: 1 0;
    }
    
    FilterPane RadioButton {
        margin: 0 0 0 2;
    }
    
    FilterPane CheckBox {
        margin: 0 0 0 2;
    }
    
    FilterPane #search-input {
        margin: 1 0;
    }
    """
    
    # Reactive filter state
    time_range = reactive("24h")
    agent_codex = reactive(True)
    agent_qwen = reactive(True)
    agent_kimi = reactive(True)
    agent_gemini = reactive(True)
    status_success = reactive(True)
    status_failed = reactive(False)
    status_interrupted = reactive(False)
    search_query = reactive("")
    
    class FilterChanged(Message):
        """Emitted when filters change."""
        def __init__(self, filters: dict):
            self.filters = filters
            super().__init__()
    
    def compose(self):
        yield Static("Filters", classes="section-title")
        
        # Time range
        with Vertical(classes="filter-section"):
            yield Static("Time Range:", classes="section-title")
            yield RadioButton("Last 24h", id="time-24h", value=True)
            yield RadioButton("Last 3 Days", id="time-3d")
            yield RadioButton("Last Week", id="time-7d")
            yield RadioButton("Custom", id="time-custom")
        
        # Agent type
        with Vertical(classes="filter-section"):
            yield Static("Agent Type:", classes="section-title")
            yield CheckBox("Codex", id="agent-codex", value=True)
            yield CheckBox("Qwen", id="agent-qwen", value=True)
            yield CheckBox("Kimi", id="agent-kimi", value=True)
            yield CheckBox("Gemini", id="agent-gemini", value=True)
        
        # Status
        with Vertical(classes="filter-section"):
            yield Static("Status:", classes="section-title")
            yield CheckBox("Success", id="status-success", value=True)
            yield CheckBox("Failed", id="status-failed")
            yield CheckBox("Interrupted", id="status-interrupted")
        
        # Search
        with Vertical(classes="filter-section"):
            yield Static("Search:", classes="section-title")
            yield Input(placeholder="Press / to search", id="search-input")
    
    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        """Handle time range radio button changes."""
        if event.value:
            if event.radio_button.id == "time-24h":
                self.time_range = "24h"
            elif event.radio_button.id == "time-3d":
                self.time_range = "3d"
            elif event.radio_button.id == "time-7d":
                self.time_range = "7d"
            elif event.radio_button.id == "time-custom":
                self.time_range = "custom"
        
        self._emit_filter_changed()
    
    def on_check_box_changed(self, event: CheckBox.Changed) -> None:
        """Handle checkbox changes."""
        if event.check_box.id == "agent-codex":
            self.agent_codex = event.value
        elif event.check_box.id == "agent-qwen":
            self.agent_qwen = event.value
        elif event.check_box.id == "agent-kimi":
            self.agent_kimi = event.value
        elif event.check_box.id == "agent-gemini":
            self.agent_gemini = event.value
        elif event.check_box.id == "status-success":
            self.status_success = event.value
        elif event.check_box.id == "status-failed":
            self.status_failed = event.value
        elif event.check_box.id == "status-interrupted":
            self.status_interrupted = event.value
        
        self._emit_filter_changed()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self.search_query = event.value
        self._emit_filter_changed()
    
    def _emit_filter_changed(self) -> None:
        """Emit filter changed message."""
        filters = {
            "time_range": self.time_range,
            "agent_types": [],
            "statuses": []
        }
        
        if self.agent_codex:
            filters["agent_types"].append("codex")
        if self.agent_qwen:
            filters["agent_types"].append("qwen")
        if self.agent_kimi:
            filters["agent_types"].append("kimi")
        if self.agent_gemini:
            filters["agent_types"].append("gemini")
        
        if self.status_success:
            filters["statuses"].append("success")
        if self.status_failed:
            filters["statuses"].append("failure")
        if self.status_interrupted:
            filters["statuses"].append("interrupted")
        
        if self.search_query:
            filters["search_query"] = self.search_query
        
        self.post_message(self.FilterChanged(filters))
    
    def get_filters(self) -> dict:
        """Get current filter state."""
        return {
            "time_range": self.time_range,
            "agent_types": [
                "codex" if self.agent_codex else None,
                "qwen" if self.agent_qwen else None,
                "kimi" if self.agent_kimi else None,
                "gemini" if self.agent_gemini else None,
            ],
            "statuses": [
                "success" if self.status_success else None,
                "failure" if self.status_failed else None,
                "interrupted" if self.status_interrupted else None,
            ],
            "search_query": self.search_query if self.search_query else None
        }
```

### Step 2: Integrate FilterPane into MainScreen

```python
# src/nexus/tui/app.py (update)
from .filter_pane import FilterPane

class MainScreen(Screen):
    """Main 3-pane TUI screen."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        # Left pane: Filters
        yield FilterPane(id="filter-pane")
        
        # ... rest of panes
```

### Step 3: Handle Filter Events

```python
# src/nexus/tui/app.py (update)
class MainScreen(Screen):
    """Main 3-pane TUI screen."""
    
    def on_filter_pane_filter_changed(self, event: FilterPane.FilterChanged) -> None:
        """Handle filter changes from FilterPane."""
        # Update stream with new filters
        self._apply_filters(event.filters)
    
    def _apply_filters(self, filters: dict) -> None:
        """Apply filters to session stream."""
        # Get filtered sessions from database
        sessions = self.app.db.get_all_sessions(filters)
        
        # Update stream pane
        stream = self.query_one("#stream-content", Static)
        stream.update(f"Found {len(sessions)} sessions")
```

## Acceptance Criteria

- [ ] FilterPane widget class
- [ ] Time range: 24h, 3 days, week, custom (RadioButtons)
- [ ] Agent checkboxes: Codex, Qwen, Kimi, Gemini
- [ ] Status checkboxes: Success, Failed, Interrupted
- [ ] Search input with / trigger
- [ ] Filter change events emitted
- [ ] CSS styling matches design
- [ ] Keyboard navigation within pane

## Next Steps

1. Update state.json: set card 05 to "completed"
2. Continue with Card 06 (Session Card)
