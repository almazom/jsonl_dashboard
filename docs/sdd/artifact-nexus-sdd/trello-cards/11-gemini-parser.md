# Card 11: Gemini JSON Parser

| Field | Value |
|-------|-------|
| **ID** | AN-11 |
| **Story Points** | 2 |
| **Depends On** | AN-01, SDD-019 (Gemini structure) |
| **Sprint** | Phase 2 |

## User Story

> As a system, I want to parse Gemini JSON session files so that session metadata can be extracted and stored in the registry.

## Context

- [requirements.md](../requirements.md) - Section 1.2 (Agent Fingerprinting)
- [gemini-structure.md](../gemini-structure.md) - Gemini JSON structure investigation
- Gemini path: `~/.gemini/tmp/{project-hash}/chats/session-*.json`
- **Format:** JSON (single object, NOT JSONL)

## Instructions

### Step 1: Understand Gemini JSON Structure

```json
{
  "sessionId": "uuid-string",
  "projectHash": "sha256-hash",
  "startTime": "2026-02-02T15:43:44.600Z",
  "lastUpdated": "2026-02-02T15:47:08.475Z",
  "messages": [
    {
      "id": "uuid",
      "timestamp": "ISO-8601",
      "type": "user" | "gemini",
      "content": "message text",
      "toolCalls": [...]  // optional
    }
  ]
}
```

**Key differences from JSONL:**
- Single JSON object (not line-delimited)
- `messages[]` array (not separate events)
- `type: "user"` or `type: "gemini"` (not `role`)
- No token count in JSON

### Step 2: Create Gemini Parser

```python
# src/nexus/parser/gemini_parser.py
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

class GeminiParser:
    """Parser for Gemini CLI JSON session files (NOT JSONL)."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data: Optional[Dict[str, Any]] = None
        self.user_prompts: List[str] = []
        self.assistant_responses: List[str] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status: str = "interrupted"
    
    def parse(self) -> Dict[str, Any]:
        """Parse JSON file and extract session metadata."""
        try:
            with open(self.filepath) as f:
                self.data = json.load(f)
            
            self._extract_messages()
            self._extract_timestamps()
            self._determine_status()
            
            return self._build_result()
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.filepath}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini session: {e}")
    
    def _extract_messages(self) -> None:
        """Extract user prompts and assistant responses."""
        messages = self.data.get("messages", [])
        
        for msg in messages:
            msg_type = msg.get("type")
            content = msg.get("content", "")
            
            if not content:
                continue
            
            if msg_type == "user":
                self.user_prompts.append(content)
            elif msg_type == "gemini":
                self.assistant_responses.append(content)
    
    def _extract_timestamps(self) -> None:
        """Extract start and end times."""
        if self.data.get("startTime"):
            self.start_time = datetime.fromisoformat(
                self.data["startTime"].replace("Z", "+00:00")
            )
        
        if self.data.get("lastUpdated"):
            self.end_time = datetime.fromisoformat(
                self.data["lastUpdated"].replace("Z", "+00:00")
            )
    
    def _determine_status(self) -> None:
        """Determine session status from last message."""
        messages = self.data.get("messages", [])
        
        if not messages:
            self.status = "interrupted"
            return
        
        last_msg = messages[-1]
        
        # Check for tool call errors
        tool_calls = last_msg.get("toolCalls", [])
        for tc in tool_calls:
            if tc.get("status") == "error":
                self.status = "failure"
                return
        
        if last_msg.get("type") == "gemini":
            self.status = "success"
        elif last_msg.get("type") == "user":
            self.status = "interrupted"
        else:
            self.status = "interrupted"
    
    def _build_result(self) -> Dict[str, Any]:
        """Build session metadata dict."""
        # Extract title from first user prompt (60 chars)
        title = "Untitled"
        if self.user_prompts:
            first_prompt = self.user_prompts[0]
            # Skip system-like prompts
            for prompt in self.user_prompts:
                if not prompt.startswith("#") and not prompt.startswith("<"):
                    title = prompt[:60].strip()
                    break
        
        # Generate summary
        summary = self._generate_summary()
        
        # Extract project name from path
        # Path format: ~/.gemini/tmp/{project-hash}/chats/session-*.json
        parts = self.filepath.parts
        project_name = "gemini-project"
        try:
            tmp_idx = parts.index("tmp")
            if tmp_idx + 1 < len(parts):
                project_hash = parts[tmp_idx + 1]
                project_name = f"gemini-{project_hash[:12]}"
        except ValueError:
            pass
        
        return {
            "filepath": str(self.filepath.absolute()),
            "project_name": project_name,
            "project_root": f"~/.gemini/tmp/{parts[-3]}",
            "agent_type": "gemini",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "summary": summary,
            "title": title,
            "model": "gemini",  # Gemini CLI uses Gemini
            "total_tokens": 0,  # Not available in JSON
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

### Step 3: Update Parser Factory

```python
# src/nexus/parser/factory.py
# Add Gemini detection

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
```

### Step 4: Write Unit Tests

```python
# tests/test_gemini_parser.py
import pytest
import json
from pathlib import Path
from src.nexus.parser.gemini_parser import GeminiParser

@pytest.fixture
def gemini_fixture_path(tmp_path):
    """Create sample Gemini JSON fixture."""
    fixture = {
        "sessionId": "test-session-123",
        "projectHash": "abc123",
        "startTime": "2026-02-17T10:00:00Z",
        "lastUpdated": "2026-02-17T10:05:00Z",
        "messages": [
            {
                "id": "msg-1",
                "timestamp": "2026-02-17T10:00:00Z",
                "type": "user",
                "content": "Fix the bug in auth.py"
            },
            {
                "id": "msg-2",
                "timestamp": "2026-02-17T10:05:00Z",
                "type": "gemini",
                "content": "I've fixed the authentication bug."
            }
        ]
    }
    
    filepath = tmp_path / "session-test.json"
    with open(filepath, "w") as f:
        json.dump(fixture, f)
    
    return str(filepath)

def test_gemini_parser_fixture(gemini_fixture_path):
    parser = GeminiParser(gemini_fixture_path)
    result = parser.parse()
    
    assert result["agent_type"] == "gemini"
    assert result["title"] == "Fix the bug in auth.py"
    assert result["status"] == "success"
    assert len(result["summary"]) > 0
```

## Acceptance Criteria

- [ ] GeminiParser class implemented
- [ ] Parses JSON (not JSONL) correctly
- [ ] Extracts user/gemini messages from messages[] array
- [ ] Generates title (60 chars max)
- [ ] Generates summary in correct format
- [ ] Determines status from last message + tool call errors
- [ ] Handles malformed JSON with clear error
- [ ] Parser factory routes Gemini files correctly
- [ ] Unit tests pass with fixture

## Next Steps

After completing this card:
1. Update state.json: set card 11 to "completed"
2. Update ssot_kanban.yaml: mark SDD-019 and Card 11 done
3. Continue with remaining parser cards (09, 10)
