# Card 10: Kimi JSONL Parser

| Field | Value |
|-------|-------|
| **ID** | AN-10 |
| **Story Points** | 2 |
| **Depends On** | AN-01 |
| **Sprint** | Phase 2 |

## User Story

> As a system, I want to parse Kimi JSONL session files so that session metadata can be extracted and stored in the registry.

## Context

- [requirements.md](../requirements.md) - Section 1.2 (Agent Fingerprinting)
- Kimi path: `~/.kimi/sessions/{session-id}/{turn-id}/context.jsonl`
- Format: JSONL (line-delimited JSON)

## Instructions

### Step 1: Understand Kimi JSONL Structure

```jsonl
{"role": "_checkpoint", "id": 0}
{"role":"user","content":"User prompt text here"}
{"role": "_checkpoint", "id": 1}
{"role":"assistant","content":"Assistant response text here"}
```

**Key fields:**
- `role`: "user" | "assistant" | "_checkpoint"
- `content`: Direct text content (not nested in parts)
- `_checkpoint`: System marker (skip these)

### Step 2: Create Kimi Parser

```python
# src/nexus/parser/kimi_parser.py
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

class KimiParser:
    """Parser for Kimi CLI JSONL session files."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.user_prompts: List[str] = []
        self.assistant_responses: List[str] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status: str = "interrupted"
        self.total_tokens: int = 0
    
    def parse(self) -> Dict[str, Any]:
        """Parse JSONL file and extract session metadata."""
        try:
            with open(self.filepath) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        self._process_event(event, line_num)
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue
            
            return self._build_result()
        
        except Exception as e:
            raise ValueError(f"Failed to parse Kimi session: {e}")
    
    def _process_event(self, event: Dict[str, Any], line_num: int) -> None:
        """Process a single JSONL event."""
        role = event.get("role")
        content = event.get("content", "")
        
        # Skip checkpoint markers
        if role == "_checkpoint":
            return
        
        # Extract content
        if role == "user" and content:
            self.user_prompts.append(content)
        elif role == "assistant" and content:
            self.assistant_responses.append(content)
    
    def _build_result(self) -> Dict[str, Any]:
        """Build session metadata dict."""
        # Extract title from first user prompt (60 chars)
        title = "Untitled"
        if self.user_prompts:
            for prompt in self.user_prompts:
                if not prompt.startswith("#") and not prompt.startswith("<"):
                    title = prompt[:60].strip()
                    break
        
        # Determine status
        if self.assistant_responses and self.user_prompts:
            self.status = "success"
        elif self.user_prompts:
            self.status = "interrupted"
        
        # Generate summary
        summary = self._generate_summary()
        
        # Extract project name from path
        # Path: ~/.kimi/sessions/{session-id}/{turn-id}/context.jsonl
        parts = self.filepath.parts
        project_name = "kimi-project"
        try:
            sessions_idx = parts.index("sessions")
            if sessions_idx + 1 < len(parts):
                session_id = parts[sessions_idx + 1]
                project_name = f"kimi-{session_id[:12]}"
        except ValueError:
            pass
        
        return {
            "filepath": str(self.filepath.absolute()),
            "project_name": project_name,
            "project_root": f"~/.kimi/sessions/{parts[-2]}",
            "agent_type": "kimi",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "summary": summary,
            "title": title,
            "model": "kimi",
            "total_tokens": 0,  # Not available in Kimi JSONL
        }
    
    def _generate_summary(self) -> str:
        """Generate session summary."""
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
        
        files = self._extract_files()
        files_str = ", ".join(files[:3]) if files else "unknown"
        status_emoji = "✅" if self.status == "success" else "⏳"
        
        return f"[{action}] {self.title[:40]} | Files: {files_str} | {status_emoji}"
    
    def _extract_files(self) -> List[str]:
        """Extract file references from prompts."""
        import re
        files = []
        for prompt in self.user_prompts[:3]:
            matches = re.findall(r'[\w./-]+\.(py|js|ts|json|yaml|yml|md)', prompt)
            files.extend(matches)
        return list(set(files))[:5]
```

### Step 3: Write Unit Tests

```python
# tests/test_kimi_parser.py
import pytest
from src.nexus.parser.kimi_parser import KimiParser

@pytest.fixture
def kimi_fixture_path(tmp_path):
    """Create sample Kimi JSONL fixture."""
    filepath = tmp_path / "context.jsonl"
    
    events = [
        '{"role": "_checkpoint", "id": 0}',
        '{"role":"user","content":"Fix the encoding issue in utils.py"}',
        '{"role": "_checkpoint", "id": 1}',
        '{"role":"assistant","content":"Fixed the UTF-8 encoding."}',
    ]
    
    with open(filepath, "w") as f:
        f.write("\n".join(events))
    
    return str(filepath)

def test_kimi_parser_fixture(kimi_fixture_path):
    parser = KimiParser(kimi_fixture_path)
    result = parser.parse()
    
    assert result["agent_type"] == "kimi"
    assert result["title"] == "Fix the encoding issue in utils.py"
    assert result["status"] == "success"
```

## Acceptance Criteria

- [ ] KimiParser class implemented
- [ ] Parses JSONL format correctly
- [ ] Extracts from role: user/assistant events
- [ ] Skips _checkpoint markers
- [ ] Handles direct content field (not nested)
- [ ] Error handling for malformed JSONL
- [ ] Unit tests pass with fixture

## Next Steps

1. Update state.json: set card 10 to "completed"
2. Update ssot_kanban.yaml: mark SDD-007 as done
3. Continue with remaining cards
