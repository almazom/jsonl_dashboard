# Card 13: Watcher Service (30s polling)

| Field | Value |
|-------|-------|
| **ID** | AN-13 |
| **Story Points** | 2 |
| **Depends On** | AN-12 (SessionScanner) |
| **Sprint** | Phase 2 |

## User Story

> As a system, I want to poll for new sessions every 30 seconds so that the UI stays up-to-date without manual refresh.

## Context

- [requirements.md](../requirements.md) - Section 1.3 (Watcher Service)

## Instructions

### Step 1: Create WatcherService Class

```python
# src/nexus/watcher/watcher_service.py
import threading
import time
from typing import Callable, Optional
from datetime import datetime

class WatcherService:
    """Background service that polls for new sessions."""
    
    def __init__(
        self,
        scanner,
        db_manager,
        polling_interval: int = 30,
        on_new_sessions: Optional[Callable] = None
    ):
        """Initialize watcher.
        
        Args:
            scanner: SessionScanner instance
            db_manager: DatabaseManager instance
            polling_interval: Seconds between polls (default: 30)
            on_new_sessions: Callback when new sessions found
        """
        self.scanner = scanner
        self.db = db_manager
        self.polling_interval = polling_interval
        self.on_new_sessions = on_new_sessions
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_poll: Optional[datetime] = None
        self._total_scanned = 0
        self._total_new = 0
    
    def start(self) -> None:
        """Start background polling thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop background polling."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
    
    def poll_now(self) -> int:
        """Trigger immediate poll.
        
        Returns:
            Number of new sessions found
        """
        return self._do_poll()
    
    def _poll_loop(self) -> None:
        """Main polling loop (runs in background thread)."""
        while self._running:
            try:
                new_count = self._do_poll()
                self._last_poll = datetime.now()
                
                if new_count > 0 and self.on_new_sessions:
                    # Callback in thread-safe way
                    self.on_new_sessions(new_count)
            
            except Exception as e:
                # Log error but continue polling
                pass
            
            # Sleep in small increments to allow clean shutdown
            for _ in range(self.polling_interval * 10):
                if not self._running:
                    break
                time.sleep(0.1)
    
    def _do_poll(self) -> int:
        """Execute single poll cycle.
        
        Returns:
            Number of new sessions found
        """
        # Scan for new sessions
        new_sessions = self.scanner.get_new_sessions()
        
        if not new_sessions:
            return 0
        
        # Insert into database
        inserted = 0
        for session in new_sessions:
            try:
                # Check if already in DB (by filepath)
                if self.db.session_exists(session["filepath"]):
                    continue
                
                self.db.insert_session(session)
                inserted += 1
                self.scanner.mark_processed(session["filepath"])
            
            except Exception as e:
                # Log error but continue with other sessions
                pass
        
        self._total_scanned += len(new_sessions)
        self._total_new += inserted
        
        return inserted
    
    def get_status(self) -> dict:
        """Get watcher status.
        
        Returns:
            Dict with watcher statistics
        """
        return {
            "running": self._running,
            "polling_interval": self.polling_interval,
            "last_poll": self._last_poll.isoformat() if self._last_poll else None,
            "total_scanned": self._total_scanned,
            "total_new": self._total_new,
        }
```

### Step 2: Integrate with TUI App

```python
# src/nexus/tui/app.py (update)
from ..watcher.watcher_service import WatcherService
from ..scanner.session_scanner import SessionScanner

class NexusApp(App):
    """Artifact Nexus TUI Application."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.scanner = None
        self.watcher = None
    
    def on_mount(self) -> None:
        """Initialize app on mount."""
        # Initialize database
        from ..db.database_manager import DatabaseManager
        from ..db.config import get_db_path
        
        self.db = DatabaseManager(get_db_path())
        
        # Initialize scanner
        self.scanner = SessionScanner()
        
        # Initialize watcher
        self.watcher = WatcherService(
            scanner=self.scanner,
            db_manager=self.db,
            polling_interval=30,
            on_new_sessions=self._on_new_sessions
        )
        
        # Start watcher
        self.watcher.start()
        
        # Initial scan
        self._do_initial_scan()
        
        # Push main screen
        self.push_screen(MainScreen())
    
    def _do_initial_scan(self) -> None:
        """Do initial scan to populate database."""
        sessions = self.scanner.scan_all()
        
        for session in sessions:
            try:
                if not self.db.session_exists(session["filepath"]):
                    self.db.insert_session(session)
                    self.scanner.mark_processed(session["filepath"])
            except:
                pass
    
    def _on_new_sessions(self, count: int) -> None:
        """Callback when new sessions found."""
        # Update UI on main thread
        def update():
            screen = self.screen
            if hasattr(screen, "_apply_filters"):
                screen._apply_filters({})  # Refresh stream
        
        self.call_from_thread(update)
    
    def on_shutdown(self) -> None:
        """Cleanup on app shutdown."""
        if self.watcher:
            self.watcher.stop()
        if self.db:
            self.db.close()
```

## Acceptance Criteria

- [ ] WatcherService class with start()/stop()
- [ ] 30-second polling interval (configurable)
- [ ] Background thread (non-blocking TUI)
- [ ] Processed files tracking
- [ ] Graceful shutdown on app exit
- [ ] Error recovery on failed polls
- [ ] Manual trigger via poll_now()
- [ ] Status reporting (get_status())

## Next Steps

1. Update state.json: set card 13 to "completed"
2. Continue with Card 14 (Filter Logic)
