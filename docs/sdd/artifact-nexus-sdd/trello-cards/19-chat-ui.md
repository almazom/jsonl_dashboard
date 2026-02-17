# Card 19: Chat UI Component

| Field | Value |
|-------|-------|
| **ID** | AN-19 |
| **Story Points** | 2 |
| **Depends On** | AN-17 (CognitiveRouter) |
| **Sprint** | Phase 3 |

## User Story

> As a user, I want an interactive chat interface so that I can ask questions about sessions and get AI-powered answers.

## Context

- [ui-flow.md](../ui-flow.md) - Section 5 (Chat Interface)

## Instructions

### Step 1: Create ChatTab Widget

```python
# src/nexus/tui/chat_tab.py
from textual.widget import Widget
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.message import Message
import asyncio

class ChatTab(Widget):
    """Chat tab with Cognitive Router integration."""
    
    CSS = """
    ChatTab {
        height: 100%;
        layout: grid;
        grid-size: 1 2;
        grid-rows: 1fr auto;
    }
    
    #chat-history {
        overflow-y: auto;
        padding: 1;
        background: $surface;
    }
    
    #chat-input-container {
        height: auto;
        padding: 1;
        background: $surface-darken-1;
    }
    
    #chat-input {
        width: 100%;
    }
    
    #send-button {
        width: auto;
        margin-left: 1;
    }
    
    .message {
        margin: 1 0;
        padding: 1;
        border: solid $primary;
    }
    
    .message-user {
        background: $primary-darken-2;
        border: solid $primary;
    }
    
    .message-assistant {
        background: $surface;
        border: solid $secondary;
    }
    
    .message-model {
        color: $text-muted;
        font-size: 80%;
    }
    """
    
    # Chat state
    messages = reactive([])
    is_loading = reactive(False)
    
    class MessageSent(Message):
        """Emitted when message is sent."""
        def __init__(self, query: str, sessions: list):
            self.query = query
            self.sessions = sessions
            super().__init__()
    
    def __init__(
        self,
        sessions: list,
        router=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.sessions = sessions
        self.router = router
        self.multi_session = len(sessions) > 1
    
    def compose(self):
        # Chat history
        with ScrollableContainer(id="chat-history"):
            yield Static("Ask a question about your sessions...", id="chat-placeholder")
        
        # Input container
        with Horizontal(id="chat-input-container"):
            yield Input(
                placeholder="Type your question...",
                id="chat-input"
            )
            yield Button("Send", id="send-button", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle send button click."""
        if event.button.id == "send-button":
            self._send_message()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        if event.input.id == "chat-input":
            self._send_message()
    
    def _send_message(self) -> None:
        """Send message to Cognitive Router."""
        input_widget = self.query_one("#chat-input", Input)
        query = input_widget.value.strip()
        
        if not query:
            return
        
        # Add user message to history
        self._add_message("user", query)
        
        # Clear input
        input_widget.value = ""
        
        # Show loading
        self.is_loading = True
        
        # Emit message sent event
        self.post_message(self.MessageSent(query, self.sessions))
    
    def _add_message(self, role: str, content: str, model: str = None) -> None:
        """Add message to chat history.
        
        Args:
            role: "user" or "assistant"
            content: Message content
            model: Model name (for assistant)
        """
        history = self.query_one("#chat-history", ScrollableContainer)
        placeholder = self.query_one("#chat-placeholder", Static)
        
        # Hide placeholder
        placeholder.display = False
        
        # Create message widget
        message_class = f"message message-{role}"
        message_html = f"<div class='{message_class}'>{content}</div>"
        
        if model:
            message_html += f"<div class='message-model'>via {model}</div>"
        
        history.mount(Static(message_html))
        
        # Scroll to bottom
        history.scroll_end()
    
    def set_answer(self, answer: str, model: str = None) -> None:
        """Set assistant answer.
        
        Args:
            answer: Answer text
            model: Model that provided answer
        """
        self._add_message("assistant", answer, model)
        self.is_loading = False
    
    def set_error(self, error: str) -> None:
        """Set error message.
        
        Args:
            error: Error text
        """
        self._add_message("assistant", f"Error: {error}")
        self.is_loading = False
    
    def update_sessions(self, sessions: list) -> None:
        """Update sessions for chat.
        
        Args:
            sessions: List of session dicts
        """
        self.sessions = sessions
        self.multi_session = len(sessions) > 1
```

### Step 2: Integrate with InspectorPane

```python
# src/nexus/tui/inspector_pane.py (update)
from .chat_tab import ChatTab

class InspectorPane(Widget):
    """Right pane inspector with tabs."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_tab: Optional[ChatTab] = None
    
    def _update_chat(self, sessions: list) -> None:
        """Update chat tab."""
        if not self.chat_tab:
            # Create chat tab on first use
            self.chat_tab = ChatTab(sessions=sessions, router=self.app.router)
            chat_container = self.query_one("#chat-content", Widget)
            chat_container.remove()
            self.mount(self.chat_tab)
        else:
            self.chat_tab.update_sessions(sessions)
    
    def on_chat_tab_message_sent(self, event: ChatTab.MessageSent) -> None:
        """Handle chat message."""
        # Query Cognitive Router
        asyncio.create_task(self._query_router(event.query, event.sessions))
    
    async def _query_router(self, query: str, sessions: list) -> None:
        """Query Cognitive Router."""
        if not self.app.router:
            self.chat_tab.set_error("Router not initialized")
            return
        
        result = await self.app.router.query(
            sessions=sessions,
            user_query=query
        )
        
        self.chat_tab.set_answer(
            answer=result["answer"],
            model=result.get("final_model")
        )
```

## Acceptance Criteria

- [ ] ChatTab widget class
- [ ] Input widget with send button
- [ ] Message history display (user/assistant)
- [ ] Streaming response handling
- [ ] Model attribution display
- [ ] Multi-session header
- [ ] Enter key to send
- [ ] Loading indicator

## Next Steps

1. Update state.json: set card 19 to "completed"
2. Continue with Card 20 (Context Loader)
