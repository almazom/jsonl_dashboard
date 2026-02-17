# Card 07: Inspector Pane Shell

| Field | Value |
|-------|-------|
| **ID** | AN-07 |
| **Story Points** | 1 |
| **Depends On** | AN-04 (Static Layout) |
| **Sprint** | Phase 1 |

## User Story

> As a user, I want an inspector pane with tabs so that I can view session details, artifacts, and chat.

## Context

- [ui-flow.md](../ui-flow.md) - Section 2 (Flow 2: Inspect)
- [requirements.md](../requirements.md) - Section 4.3 (Inspector Tabs)

## Instructions

### Step 1: Create InspectorPane Widget

```python
# src/nexus/tui/inspector_pane.py
from textual.widget import Widget
from textual.widgets import Static, TabbedContent, TabPane
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

class InspectorPane(Widget):
    """Right pane inspector with tabs."""
    
    CSS = """
    InspectorPane {
        height: 100%;
        padding: 0;
    }
    
    InspectorPane TabbedContent {
        height: 100%;
    }
    
    InspectorPane .tab-content {
        padding: 1;
        overflow-y: auto;
    }
    
    InspectorPane .detail-row {
        margin: 1 0;
    }
    
    InspectorPane .detail-label {
        text-style: bold;
        width: 15;
    }
    
    InspectorPane .multi-session-header {
        background: $primary;
        color: $text;
        padding: 1;
        text-align: center;
    }
    """
    
    # Current session data
    sessions = reactive([])
    is_multi_session = reactive(False)
    
    def compose(self):
        yield Static("Inspector", id="inspector-title")
        
        with TabbedContent(id="inspector-tabs"):
            # Tab 1: Details
            with TabPane("Details", id="tab-details"):
                with Vertical(classes="tab-content"):
                    yield Static("No session selected", id="details-content")
            
            # Tab 2: Artifacts
            with TabPane("Artifacts", id="tab-artifacts"):
                with Vertical(classes="tab-content"):
                    yield Static("Select a session to view artifacts", id="artifacts-content")
            
            # Tab 3: Chat
            with TabPane("Chat", id="tab-chat"):
                with Vertical(classes="tab-content"):
                    yield Static("Select a session to chat", id="chat-placeholder")
    
    def watch_sessions(self, sessions: list) -> None:
        """Update inspector when sessions change."""
        self.is_multi_session = len(sessions) > 1
        self._update_details(sessions)
        self._update_artifacts(sessions)
        self._update_chat(sessions)
    
    def _update_details(self, sessions: list) -> None:
        """Update details tab."""
        content = self.query_one("#details-content", Static)
        
        if not sessions:
            content.update("No session selected")
            return
        
        if self.is_multi_session:
            # Multi-session view
            html = f"<div class='multi-session-header'>{len(sessions)} sessions selected</div>"
            for session in sessions:
                html += f"""
                <div class='detail-row'>
                    <span class='detail-label'>Project:</span> {session.get('project_name', 'unknown')}<br/>
                    <span class='detail-label'>Status:</span> {session.get('status', 'unknown')}<br/>
                    <span class='detail-label'>Agent:</span> {session.get('agent_type', 'unknown')}<br/>
                    ---
                </div>
                """
            content.update(html)
        else:
            # Single session view
            session = sessions[0]
            html = f"""
            <div class='detail-row'>
                <span class='detail-label'>Title:</span> {session.get('title', 'Untitled')}
            </div>
            <div class='detail-row'>
                <span class='detail-label'>Project:</span> {session.get('project_name', 'unknown')}
            </div>
            <div class='detail-row'>
                <span class='detail-label'>Agent:</span> {session.get('agent_type', 'unknown')}
            </div>
            <div class='detail-row'>
                <span class='detail-label'>Model:</span> {session.get('model', 'unknown')}
            </div>
            <div class='detail-row'>
                <span class='detail-label'>Status:</span> {session.get('status', 'unknown')}
            </div>
            <div class='detail-row'>
                <span class='detail-label'>Start:</span> {session.get('start_time', 'unknown')}
            </div>
            <div class='detail-row'>
                <span class='detail-label'>End:</span> {session.get('end_time', 'unknown')}
            </div>
            <div class='detail-row'>
                <span class='detail-label'>Summary:</span><br/>{session.get('summary', '')}
            </div>
            """
            content.update(html)
    
    def _update_artifacts(self, sessions: list) -> None:
        """Update artifacts tab."""
        content = self.query_one("#artifacts-content", Static)
        
        if not sessions:
            content.update("Select a session to view artifacts")
            return
        
        # Extract files from session summaries
        files = set()
        for session in sessions:
            summary = session.get("summary", "")
            # Extract files from "Files: file1.py, file2.js" pattern
            if "Files:" in summary:
                files_part = summary.split("Files:")[1].split("|")[0].strip()
                for f in files_part.split(","):
                    files.add(f.strip())
        
        if files:
            html = "<div class='tab-content'><strong>Files mentioned:</strong><br/>"
            for f in sorted(files):
                html += f"• {f}<br/>"
            html += "</div>"
            content.update(html)
        else:
            content.update("No artifacts found")
    
    def _update_chat(self, sessions: list) -> None:
        """Update chat tab."""
        placeholder = self.query_one("#chat-placeholder", Static)
        
        if not sessions:
            placeholder.update("Select a session to chat")
            return
        
        if self.is_multi_session:
            placeholder.update(f"Chat with {len(sessions)} sessions\n\nType your question below...")
        else:
            placeholder.update(f"Chat: {sessions[0].get('title', 'Untitled')}\n\nType your question below...")
    
    def load_sessions(self, sessions: list) -> None:
        """Load sessions into inspector."""
        self.sessions = sessions
```

### Step 2: Integrate into MainScreen

```python
# src/nexus/tui/app.py (update)
from .inspector_pane import InspectorPane

class MainScreen(Screen):
    """Main 3-pane TUI screen."""
    
    def __init__(self):
        super().__init__()
        self.selected_session_ids: set[int] = set()
    
    def on_session_card_selected(self, event: SessionCard.Selected) -> None:
        """Handle session selection."""
        if event.selected:
            self.selected_session_ids.add(event.session_id)
        else:
            self.selected_session_ids.discard(event.session_id)
        
        self._update_status_bar()
    
    def on_key(self, event) -> None:
        """Handle global key events."""
        if event.key == "q":
            self.exit()
        elif event.key == "enter":
            self._open_inspector()
        elif event.key == "c":
            self._clear_selections()
    
    def _open_inspector(self) -> None:
        """Open inspector with selected or focused session."""
        if self.selected_session_ids:
            # Multi-session mode
            sessions = self.app.db.get_sessions_by_ids(list(self.selected_session_ids))
        else:
            # Single session (focused)
            focused = self.focus
            if hasattr(focused, "session_id"):
                sessions = [self.app.db.get_session(focused.session_id)]
            else:
                return
        
        # Update inspector
        inspector = self.query_one(InspectorPane)
        inspector.load_sessions(sessions)
    
    def _clear_selections(self) -> None:
        """Clear all selections."""
        self.selected_session_ids.clear()
        
        # Clear card selections
        for card in self.query(SessionCard):
            card.selected = False
        
        self._update_status_bar()
```

## Acceptance Criteria

- [ ] InspectorPane widget class
- [ ] 3 tabs: Details (1), Artifacts (2), Chat (3)
- [ ] Tab switching with number keys
- [ ] Content area for each tab
- [ ] Multi-session header when applicable
- [ ] Details tab shows session metadata
- [ ] Artifacts tab shows mentioned files
- [ ] Chat tab shows placeholder
- [ ] Close handler (Esc key)

## Next Steps

1. Update state.json: set card 07 to "completed"
2. Update ssot_kanban.yaml: mark SDD-003, SDD-004, SDD-005 as done
3. Continue with Card 12 (SessionScanner)
