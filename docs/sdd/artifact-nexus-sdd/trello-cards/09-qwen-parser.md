# Card 09: Qwen JSONL Parser

| Field | Value |
|-------|-------|
| **ID** | AN-09 |
| **Story Points** | 2 |
| **Depends On** | AN-01 |
| **Sprint** | Phase 2 |

## User Story

> As a system, I want to parse Qwen JSONL session files so that session metadata can be extracted and stored in the registry.

## Context

- [requirements.md](../requirements.md) - Section 1.2 (Agent Fingerprinting)
- Qwen path: `~/.qwen/projects/{project}/chats/{session-id}.jsonl`
- Format: JSONL (line-delimited JSON)

## Instructions

### Step 1: Understand Qwen JSONL Structure

```jsonl
{"uuid":"...", "type":"system", "cwd":"/path", "model":"...", ...}
{"uuid":"...", "type":"user", "message":{"role":"user", "parts":[{"text":"prompt"}]}}
{"uuid":"...", "type":"assistant", "model":"...", "message":{"role":"model", "parts":[{"text":"response"}]}}
{"uuid":"...", "type":"system", "subtype":"ui_telemetry", "systemPayload":{...}}
```

**Key fields:**
- `type`: "system" | "user" | "assistant"
- `cwd`: Working directory (project root)
- `model`: Model name
- `message.parts[].text`: Content for user/assistant

### Step 2: Create Qwen Parser

```python
# src/nexus/parser/qwen_parser.py
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

class QwenParser:
    """Parser for Qwen CLI JSONL session files."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
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
        try:
            with open(self.filepath) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    event = json.loads(line)
                    self._process_event(event)
            
            return self._build_result()
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSONL in {self.filepath}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse Qwen session: {e}")
    
    def _process_event(self, event: Dict[str, Any]) -> None:
        """Process a single JSONL event."""
        event_type = event.get("type")
        timestamp = event.get("timestamp")
        
        # Track timestamps
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if self.start_time is None:
                    self.start_time = dt
                self.end_time = dt
            except:
                pass
        
        if event_type == "system":
            self.cwd = event.get("cwd", self.cwd)
            self.model = event.get("model", self.model)
        
        elif event_type == "user":
            message = event.get("message", {})
            parts = message.get("parts", [])
            for part in parts:
                text = part.get("text", "")
                if text:
                    self.user_prompts.append(text)
        
        elif event_type == "assistant":
            self.model = event.get("model", self.model)
            message = event.get("message", {})
            parts = message.get("parts", [])
            for part in parts:
                text = part.get("text", "")
                if text:
                    self.assistant_responses.append(text)
            
            # Check for usage metadata
            usage = event.get("usageMetadata", {})
            total = usage.get("totalTokenCount", 0)
            if total > 0:
                self.total_tokens = total
    
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
        project_name = "qwen-project"
        if self.cwd:
            project_name = Path(self.cwd).name
        
        return {
            "filepath": str(self.filepath.absolute()),
            "project_name": project_name,
            "project_root": self.cwd or "unknown",
            "agent_type": "qwen",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "summary": summary,
            "title": title,
            "model": self.model or "unknown",
            "total_tokens": self.total_tokens,
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
# tests/test_qwen_parser.py
import pytest
from src.nexus.parser.qwen_parser import QwenParser

@pytest.fixture
def qwen_fixture_path(tmp_path):
    """Create sample Qwen JSONL fixture."""
    filepath = tmp_path / "session.jsonl"
    
    events = [
        '{"uuid":"1", "type":"system", "cwd":"/test/project", "model":"qwen-max"}',
        '{"uuid":"2", "type":"user", "message":{"role":"user", "parts":[{"text":"Add tests for auth.py"}]}}',
        '{"uuid":"3", "type":"assistant", "model":"qwen-max", "message":{"role":"model", "parts":[{"text":"Tests added."}]}, "usageMetadata":{"totalTokenCount":1500}}',
    ]
    
    with open(filepath, "w") as f:
        f.write("\n".join(events))
    
    return str(filepath)

def test_qwen_parser_fixture(qwen_fixture_path):
    parser = QwenParser(qwen_fixture_path)
    result = parser.parse()
    
    assert result["agent_type"] == "qwen"
    assert result["title"] == "Add tests for auth.py"
    assert result["status"] == "success"
    assert result["total_tokens"] == 1500
```

## Acceptance Criteria

- [ ] QwenParser class implemented
- [ ] Parses JSONL format correctly
- [ ] Extracts from type: user/assistant/system events
- [ ] Handles message.parts[].text structure
- [ ] Extracts cwd, model from system events
- [ ] Extracts tokens from usageMetadata
- [ ] Error handling for malformed JSONL
- [ ] Unit tests pass with fixture

## Next Steps

1. Update state.json: set card 09 to "completed"
2. Continue with Card 10 (Kimi parser)
