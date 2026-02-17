# Card 04: Static 3-Pane Layout

| Field | Value |
|-------|-------|
| **ID** | AN-04 |
| **Story Points** | 3 |
| **Depends On** | AN-03 (DatabaseManager) |
| **Sprint** | Phase 1 |

## User Story

> As a user, I want a 3-pane TUI layout so that I can see filters, session stream, and session details simultaneously.

## Context

- [ui-flow.md](../ui-flow.md) - UI specifications
- [requirements.md](../requirements.md) - Section 4 (User Interface)
- Minimum terminal size: 120x30

## Instructions

### Step 1: Create Main TUI Application

```python
# src/nexus/tui/app.py
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Label

class MainScreen(Screen):
    """Main 3-pane TUI screen."""
    
    CSS = """
    MainScreen {
        layout: grid;
        grid-size: 3 1;
        grid-columns: 20fr 45fr 35fr;
        grid-rows: 1fr;
    }
    
    #filter-pane {
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    #stream-pane {
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    #inspector-pane {
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    #status-bar {
        dock: bottom;
        background: $primary;
        color: $text;
        padding: 0 2;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        # Left pane: Filters
        with Container(id="filter-pane"):
            yield Static("Filters", id="filter-title")
            yield Static("Time Range:\n  [ ] Last 24h\n  [ ] Last 3 Days\n  [ ] Last Week", id="time-filters")
            yield Static("Agent Type:\n  [x] Codex\n  [x] Qwen\n  [x] Kimi\n  [x] Gemini", id="agent-filters")
            yield Static("Status:\n  [x] Success\n  [ ] Failed\n  [ ] Interrupted", id="status-filters")
            yield Static("Search: /", id="search-prompt")
        
        # Center pane: Event Stream
        with ScrollableContainer(id="stream-pane"):
            yield Static("Event Stream", id="stream-title")
            yield Static("Loading sessions...", id="stream-content")
        
        # Right pane: Inspector
        with Container(id="inspector-pane"):
            yield Static("Inspector", id="inspector-title")
            yield Static("Select a session", id="inspector-content")
        
        # Status bar
        yield Static("Artifact Nexus - 0 sessions", id="status-bar")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize screen."""
        self.set_interval(0.1, self._update_status)
    
    def _update_status(self) -> None:
        """Update status bar."""
        status = self.query_one("#status-bar", Static)
        status.update("Artifact Nexus - Ready")


class NexusApp(App):
    """Artifact Nexus TUI Application."""
    
    CSS = """
    Screen {
        background: $background;
    }
    """
    
    def on_mount(self) -> None:
        """Push main screen on mount."""
        self.push_screen(MainScreen())
    
    def on_key(self, event) -> None:
        """Handle global key events."""
        if event.key == "q":
            self.exit()
        elif event.key == "ctrl+c":
            self.exit()


def main():
    """Entry point for nexus CLI."""
    app = NexusApp()
    app.run()


if __name__ == "__main__":
    main()
```

### Step 2: Update CLI Entry Point

```python
# src/nexus/cli.py
import argparse
from .tui.app import NexusApp

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="nexus",
        description="Artifact Nexus - Terminal observability for AI agents"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    parser.add_argument(
        "--no-watch",
        action="store_true",
        help="Disable Watcher polling"
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["add", "scan", "doctor"],
        help="Command to run"
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path for add command"
    )
    
    args = parser.parse_args()
    
    if args.command:
        # CLI commands (to be implemented)
        print(f"Command {args.command} not yet implemented")
    else:
        # Launch TUI
        app = NexusApp()
        app.run()


if __name__ == "__main__":
    main()
```

### Step 3: Add TCSS File

```css
/* src/nexus/tui/main.tcss */

/* Responsive breakpoints */
@media (max-width: 100) {
    MainScreen {
        grid-size: 1 3;
        grid-columns: 1fr;
        grid-rows: 1fr 1fr 1fr;
    }
}

@media (max-width: 60) {
    /* Mobile: stack vertically */
    MainScreen {
        grid-size: 1 4;
    }
}

/* Minimum terminal size warning */
#size-warning {
    display: none;
    background: $error;
    color: $text;
    padding: 2;
}

@media (max-width: 120) or (height < 30) {
    #size-warning {
        display: block;
    }
}
```

### Step 4: Verify Installation

```bash
cd /home/pets/temp/jsonl_dashboard

# Run TUI
poetry run python -m src.nexus.tui.app

# Or via CLI
poetry run nexus
```

## Acceptance Criteria

- [ ] MainScreen class extending textual.screen.Screen
- [ ] 3-pane layout: Filters (20%), Stream (45%), Inspector (35%)
- [ ] TCSS file with responsive breakpoints
- [ ] Minimum terminal size: 120x30 (warning if smaller)
- [ ] Keyboard handler for q (quit)
- [ ] Status bar showing app status
- [ ] Header and Footer widgets
- [ ] No Textual errors on launch
- [ ] Clean exit on 'q' or Ctrl+C

## Next Steps

After completing this card:
1. Update state.json: set card 04 to "completed"
2. Update ssot_kanban.yaml: mark SDD-002 as done
3. Read next card: [05-filter-pane.md](./05-filter-pane.md)
4. Continue execution
