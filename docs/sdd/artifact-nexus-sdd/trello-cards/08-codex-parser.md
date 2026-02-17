# Card 08: Codex JSONL Parser

| Field | Value |
|-------|-------|
| **ID** | AN-08 |
| **Story Points** | 3 |
| **Depends On** | AN-07 |
| **Sprint** | Phase 2 |

## User Story

> As a system, I want to parse Codex JSONL session files so that session metadata can be extracted and stored in the registry.

## Context

- [requirements.md](../requirements.md) - Section 1.2 (Agent Fingerprinting)
- [Interview Log](../gaps.md) - Session paths for Codex
- Codex path: `~/.codex/sessions/2026/{MM}/{DD}/rollout-*.jsonl`

## Instructions

### Step 1: Study Codex JSONL Structure

Key event types in Codex JSONL:
- `session_meta` - Session metadata
- `response_item` (role: user) - User prompts
- `response_item` (role: assistant) - Agent responses
- `turn_context` - Turn context with model, cwd
- `event_msg` (type: token_count) - Token usage
- `event_msg` (type: task_completed) - Session end

### Step 2: Create Codex Parser

```python
# src/nexus/parser/codex_parser.py
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

class CodexParser:
    """Parser for Codex CLI JSONL session files."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.events: List[Dict[str, Any]] = []
        self.user_prompts: List[str] = []
        self.assistant_responses: List[str] = []
        self.cwd: Optional[str] = None
        self.model: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status: str = "interrupted"
        self.total_tokens: int = 0
    
    def parse(self) -> Dict[str, Any]:
        """Parse JSONL file and extract session metadata."""
        with open(self.filepath) as f:
            for line in f:
                event = json.loads(line.strip())
                self._process_event(event)
        
        return self._build_result()
    
    def _process_event(self, event: Dict[str, Any]) -> None:
        """Process a single JSONL event."""
        event_type = event.get("type")
        payload = event.get("payload", {})
        timestamp = event.get("timestamp")
        
        # Track timestamps
        if timestamp:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if self.start_time is None:
                self.start_time = dt
            self.end_time = dt
        
        if event_type == "session_meta":
            self.cwd = payload.get("cwd")
            self.model = payload.get("model_provider")
        
        elif event_type == "response_item":
            role = payload.get("role")
            content = payload.get("content", [])
            text = content[0].get("text", "") if content else ""
            
            if role == "user" and text:
                self.user_prompts.append(text)
            elif role == "assistant" and text:
                self.assistant_responses.append(text)
        
        elif event_type == "turn_context":
            self.cwd = payload.get("cwd", self.cwd)
            self.model = payload.get("model", self.model)
        
        elif event_type == "event_msg":
            msg_type = payload.get("type")
            if msg_type == "token_count":
                info = payload.get("info", {})
                usage = info.get("total_token_usage", {})
                self.total_tokens = usage.get("total_tokens", 0)
            elif msg_type == "task_completed":
                self.status = "success"
    
    def _build_result(self) -> Dict[str, Any]:
        """Build session metadata dict."""
        # Extract title from first user prompt (60 chars)
        title = "Untitled"
        if self.user_prompts:
            first_prompt = self.user_prompts[0]
            # Skip system instructions, find first real prompt
            for prompt in self.user_prompts:
                if not prompt.startswith("#") and not prompt.startswith("<"):
                    title = prompt[:60].strip()
                    break
        
        # Generate summary
        summary = self._generate_summary()
        
        return {
            "filepath": str(self.filepath.absolute()),
            "project_name": Path(self.cwd).name if self.cwd else "unknown",
            "project_root": self.cwd or "unknown",
            "agent_type": "codex",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "summary": summary,
            "title": title,
            "model": self.model,
            "total_tokens": self.total_tokens,
        }
    
    def _generate_summary(self) -> str:
        """Generate session summary."""
        # Extract action verb from first prompt
        action = "WORK"
        if self.user_prompts:
            prompt_lower = self.user_prompts[0].lower()
            if "fix" in prompt_lower:
                action = "FIX"
            elif "add" in prompt_lower or "create" in prompt_lower:
                action = "ADD"
            elif "remove" in prompt_lower or "delete" in prompt_lower:
                action = "REMOVE"
            elif "test" in prompt_lower:
                action = "TEST"
        
        # Extract mentioned files
        files = self._extract_files()
        files_str = ", ".join(files[:3]) if files else "unknown"
        
        status_emoji = "✅" if self.status == "success" else "⏳"
        
        return f"[{action}] {self.title[:40]} | Files: {files_str} | {status_emoji}"
    
    def _extract_files(self) -> List[str]:
        """Extract file references from prompts."""
        import re
        files = []
        for prompt in self.user_prompts[:3]:
            # Match .py, .js, .ts, .json, .yaml, .md files
            matches = re.findall(r'[\w./-]+\.(py|js|ts|json|yaml|yml|md)', prompt)
            files.extend(matches)
        return list(set(files))[:5]
```

### Step 3: Create Parser Factory

```python
# src/nexus/parser/factory.py
from pathlib import Path
from .codex_parser import CodexParser

def get_parser(filepath: str):
    """Get appropriate parser based on file path/content."""
    path = Path(filepath)
    
    # Check by path pattern
    if ".codex" in str(path):
        return CodexParser(filepath)
    elif ".qwen" in str(path):
        from .qwen_parser import QwenParser
        return QwenParser(filepath)
    elif ".kimi" in str(path):
        from .kimi_parser import KimiParser
        return KimiParser(filepath)
    elif ".gemini" in str(path):
        from .gemini_parser import GeminiParser
        return GeminiParser(filepath)
    
    # Fallback: try to detect from content
    return _detect_by_content(filepath)

def _detect_by_content(filepath: str):
    """Detect parser by reading first line of file."""
    with open(filepath) as f:
        first_line = f.readline()
    
    if "session_meta" in first_line:
        return CodexParser(filepath)
    # Add more detection logic
    
    # Unknown format
    from .codex_parser import CodexParser  # Default to Codex-like parser
    return CodexParser(filepath)
```

### Step 4: Write Unit Tests

```python
# tests/test_codex_parser.py
import pytest
from src.nexus.parser.codex_parser import CodexParser

def test_codex_parser_fixture(codex_fixture_path):
    parser = CodexParser(codex_fixture_path)
    result = parser.parse()
    
    assert result["agent_type"] == "codex"
    assert result["title"] != ""
    assert result["status"] in ("success", "failure", "interrupted")
```

## Acceptance Criteria

- [ ] CodexParser class implemented
- [ ] Parses all event types correctly
- [ ] Extracts user prompts and assistant responses
- [ ] Generates title (60 chars max)
- [ ] Generates summary in correct format
- [ ] Extracts file references
- [ ] Determines status from task_completed event
- [ ] Parser factory routes Codex files correctly
- [ ] Unit tests pass

## Next Steps

After completing this card:
1. Update state.json: set card 08 to "completed"
2. Read next card: [09-qwen-parser.md](./09-qwen-parser.md)
3. Continue execution (Qwen, Kimi, Gemini parsers can be done in parallel)
