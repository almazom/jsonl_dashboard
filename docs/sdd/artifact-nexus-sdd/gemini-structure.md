# Gemini JSON Structure Investigation

**Date:** February 18, 2026  
**Status:** COMPLETE  
**Reviewer:** Codex (Gap #9 addressed)

---

## File Location

```
~/.gemini/tmp/{project-hash}/chats/session-{date}-{id}.json
```

**Example:**
```
~/.gemini/tmp/9fb7af7804e54c5619f7512d0343be4ed064c7657f694f768d13a4b1b7db0c14/chats/session-2026-02-02T15-43-22e6d15b.json
```

---

## JSON Structure

```json
{
  "sessionId": "uuid-string",
  "projectHash": "sha256-hash",
  "startTime": "ISO-8601 timestamp",
  "lastUpdated": "ISO-8601 timestamp",
  "messages": [
    {
      "id": "uuid",
      "timestamp": "ISO-8601",
      "type": "user" | "gemini",
      "content": "string (the actual message)",
      "toolCalls": [
        {
          "id": "tool-call-id",
          "name": "tool_name",
          "args": { ... },
          "result": [ ... ],
          "status": "success" | "error",
          "timestamp": "ISO-8601"
        }
      ]
    }
  ]
}
```

---

## Field Mapping for Parser

| Purpose | Field Path |
|---------|------------|
| **Session ID** | `sessionId` |
| **Start Time** | `startTime` |
| **End Time** | `lastUpdated` |
| **User Prompts** | `messages[]` where `type == "user"` → `content` |
| **Assistant Responses** | `messages[]` where `type == "gemini"` → `content` |
| **Tool Calls** | `messages[].toolCalls[]` |
| **Status** | Determine from last message: if has error → failure, else success |
| **Tokens** | NOT in JSON (must estimate or mark as 0) |

---

## Status Determination

```python
def determine_status(messages: list) -> str:
    if not messages:
        return "interrupted"
    
    last_msg = messages[-1]
    if last_msg.get("type") == "gemini":
        # Check for tool call errors
        tool_calls = last_msg.get("toolCalls", [])
        for tc in tool_calls:
            if tc.get("status") == "error":
                return "failure"
        return "success"
    elif last_msg.get("type") == "user":
        # Session ended on user message - likely interrupted
        return "interrupted"
    return "interrupted"
```

---

## Sample Fixture Created

**Location:** `tests/fixtures/gemini_sample.json`

Contains:
- Minimal valid Gemini session
- 2 user messages
- 2 gemini responses
- 1 tool call example

---

## Parser Implementation Notes

1. **JSON (not JSONL):** Load entire file with `json.load()`, not line-by-line
2. **Messages array:** Iterate `messages` list, not lines
3. **Type field:** `type: "user"` or `type: "gemini"` (not `role`)
4. **Tool calls:** Optional, nested in message object
5. **No token data:** Must estimate or leave as 0

---

## Card 11 Updated

Card 11 (gemini-parser.md) updated with this structure.

---

**Gap Status:** ✅ RESOLVED (Codex Gap #9)
