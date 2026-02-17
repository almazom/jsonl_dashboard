# Card 12: SessionScanner

| Field | Value |
|-------|-------|
| **ID** | AN-12 |
| **Story Points** | 3 |
| **Depends On** | AN-08, AN-09, AN-10, AN-11 (All Parsers) |
| **Sprint** | Phase 2 |

## User Story

> As a system, I want to scan directories for session files so that I can discover and index all agent sessions.

## Context

- [requirements.md](../requirements.md) - Section 1.1 (Session Sources)
- Session paths for all 4 agents

## Instructions

### Step 1: Create SessionScanner Class

```python
# src/nexus/scanner/session_scanner.py
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from datetime import datetime
import hashlib

class SessionScanner:
    """Scans directories for agent session files."""
    
    # Agent session patterns
    AGENT_PATHS = {
        "codex": "~/.codex/sessions/2026/*/*/*.jsonl",
        "qwen": "~/.qwen/projects/*/chats/*.jsonl",
        "kimi": "~/.kimi/sessions/*/*/context.jsonl",
        "gemini": "~/.gemini/tmp/*/chats/*.json",
    }
    
    def __init__(self, custom_paths: Optional[List[str]] = None):
        """Initialize scanner.
        
        Args:
            custom_paths: Optional list of additional paths to scan
        """
        self.custom_paths = custom_paths or []
        self.processed_files: Set[str] = set()
        self.file_hashes: Dict[str, str] = {}
    
    def scan_all(self) -> List[Dict[str, Any]]:
        """Scan all agent paths for session files.
        
        Returns:
            List of session metadata dicts
        """
        sessions = []
        
        # Scan default agent paths
        for agent, pattern in self.AGENT_PATHS.items():
            sessions.extend(self._scan_pattern(pattern, agent))
        
        # Scan custom paths
        for custom_path in self.custom_paths:
            sessions.extend(self._scan_custom(custom_path))
        
        # Deduplicate by filepath
        seen = set()
        unique_sessions = []
        for session in sessions:
            if session["filepath"] not in seen:
                seen.add(session["filepath"])
                unique_sessions.append(session)
        
        return unique_sessions
    
    def _scan_pattern(self, pattern: str, agent: str) -> List[Dict[str, Any]]:
        """Scan glob pattern for session files.
        
        Args:
            pattern: Glob pattern (e.g., ~/.codex/sessions/*/*/*.jsonl)
            agent: Agent type name
            
        Returns:
            List of session metadata dicts
        """
        sessions = []
        path = Path(pattern.replace("~", str(Path.home())))
        
        try:
            for filepath in path.parent.glob(path.name):
                if not filepath.is_file():
                    continue
                
                # Check if already processed
                if str(filepath) in self.processed_files:
                    continue
                
                # Parse session
                session = self._parse_session(filepath, agent)
                if session:
                    sessions.append(session)
                    self.processed_files.add(str(filepath))
        except Exception as e:
            # Log error but continue scanning
            pass
        
        return sessions
    
    def _scan_custom(self, custom_path: str) -> List[Dict[str, Any]]:
        """Scan custom path for session files.
        
        Args:
            custom_path: Custom directory or file path
            
        Returns:
            List of session metadata dicts
        """
        sessions = []
        path = Path(custom_path.replace("~", str(Path.home())))
        
        if path.is_file():
            # Single file - detect agent type
            agent = self._detect_agent(path)
            session = self._parse_session(path, agent)
            if session:
                sessions.append(session)
                self.processed_files.add(str(path))
        elif path.is_dir():
            # Directory - recursive scan
            for ext in ["*.jsonl", "*.json"]:
                for filepath in path.rglob(ext):
                    if str(filepath) in self.processed_files:
                        continue
                    
                    agent = self._detect_agent(filepath)
                    session = self._parse_session(filepath, agent)
                    if session:
                        sessions.append(session)
                        self.processed_files.add(str(filepath))
        
        return sessions
    
    def _detect_agent(self, filepath: Path) -> str:
        """Detect agent type from file path.
        
        Args:
            filepath: Path to session file
            
        Returns:
            Agent type string
        """
        path_str = str(filepath).lower()
        
        if ".codex" in path_str:
            return "codex"
        elif ".qwen" in path_str:
            return "qwen"
        elif ".kimi" in path_str:
            return "kimi"
        elif ".gemini" in path_str:
            return "gemini"
        else:
            return "unknown"
    
    def _parse_session(self, filepath: Path, agent: str) -> Optional[Dict[str, Any]]:
        """Parse session file and extract metadata.
        
        Args:
            filepath: Path to session file
            agent: Agent type
            
        Returns:
            Session metadata dict or None on error
        """
        try:
            from nexus.parser.factory import get_parser
            
            parser = get_parser(str(filepath))
            session_data = parser.parse()
            
            # Add unique ID
            session_data["id"] = self._compute_file_hash(filepath)
            
            return session_data
        
        except Exception as e:
            # Log error but continue
            return None
    
    def _compute_file_hash(self, filepath: Path) -> str:
        """Compute content hash for deduplication.
        
        Args:
            filepath: Path to file
            
        Returns:
            SHA256 hash of first 1KB
        """
        hasher = hashlib.sha256()
        
        with open(filepath, "rb") as f:
            # Hash first 1KB for quick dedup
            hasher.update(f.read(1024))
        
        return hasher.hexdigest()[:16]
    
    def get_new_sessions(self) -> List[Dict[str, Any]]:
        """Get only new sessions since last scan.
        
        Returns:
            List of new session metadata dicts
        """
        all_sessions = self.scan_all()
        
        # Filter to only new ones
        new_sessions = []
        for session in all_sessions:
            if session["filepath"] not in self.processed_files:
                new_sessions.append(session)
        
        return new_sessions
    
    def mark_processed(self, filepath: str) -> None:
        """Mark a file as processed.
        
        Args:
            filepath: Absolute file path
        """
        self.processed_files.add(filepath)
```

### Step 2: Write Unit Tests

```python
# tests/test_session_scanner.py
import pytest
from src.nexus.scanner.session_scanner import SessionScanner

def test_scanner_initialization():
    scanner = SessionScanner()
    assert scanner.processed_files == set()

def test_detect_agent():
    scanner = SessionScanner()
    
    assert scanner._detect_agent(type('Path', (), {'__str__': lambda s: '/home/.codex/session.jsonl'})()) == "codex"
    assert scanner._detect_agent(type('Path', (), {'__str__': lambda s: '/home/.qwen/session.jsonl'})()) == "qwen"
```

## Acceptance Criteria

- [ ] SessionScanner class
- [ ] Scan all 4 agent paths
- [ ] File pattern matching per agent
- [ ] Deduplication by filepath hash
- [ ] New vs existing session detection
- [ ] Error handling for permission issues
- [ ] Progress logging
- [ ] Custom path support

## Next Steps

1. Update state.json: set card 12 to "completed"
2. Continue with Card 13 (Watcher Service)
