# Card 17: CognitiveRouter Class

| Field | Value |
|-------|-------|
| **ID** | AN-17 |
| **Story Points** | 3 |
| **Depends On** | AN-16 (chains.yaml Parser) |
| **Sprint** | Phase 3 |

## User Story

> As a system, I want to query sessions with AI using a fallback chain of models so that users can get answers even if some models are unavailable.

## Context

- [requirements.md](../requirements.md) - Section 5 (Cognitive Router)

## Instructions

### Step 1: Create CognitiveRouter Class

```python
# src/nexus/router/cognitive_router.py
import asyncio
import os
from typing import List, Dict, Any, Optional
from .chains_config import ChainsConfig, ModelConfig, ChainConfig

class CognitiveRouter:
    """AI chat engine with fallback chain."""
    
    def __init__(self, chains_config: ChainsConfig, db_manager=None):
        """Initialize router.
        
        Args:
            chains_config: ChainsConfig instance
            db_manager: Optional DatabaseManager for audit logging
        """
        self.config = chains_config
        self.db = db_manager
    
    async def query(
        self,
        sessions: List[Dict[str, Any]],
        user_query: str,
        chain_name: str = "default"
    ) -> Dict[str, Any]:
        """Query sessions with fallback chain.
        
        Args:
            sessions: List of session dicts to query
            user_query: User's question
            chain_name: Name of chain to use
            
        Returns:
            Dict with answer, final_model, chain_log
        """
        chain = self.config.get_chain(chain_name)
        
        if not chain.models:
            return {
                "answer": "No models configured in chain",
                "final_model": None,
                "chain_log": ["No models in chain"]
            }
        
        chain_log = []
        final_model = None
        answer = None
        
        # Build context from sessions
        context = self._build_context(sessions)
        
        # Try each model in chain
        for model_config in chain.models:
            try:
                answer = await self._query_model(
                    model_config=model_config,
                    context=context,
                    user_query=user_query
                )
                
                final_model = model_config.name
                chain_log.append(f"{model_config.name}: success")
                break
            
            except AuthError as e:
                chain_log.append(f"{model_config.name}: auth failed ({e})")
                # Don't retry on auth error
                continue
            
            except RateLimitError as e:
                chain_log.append(f"{model_config.name}: rate limited")
                continue
            
            except TimeoutError as e:
                chain_log.append(f"{model_config.name}: timeout")
                continue
            
            except Exception as e:
                chain_log.append(f"{model_config.name}: failed ({e})")
                continue
        
        # Log to audit
        if self.db and final_model:
            session_ids = [s["id"] for s in sessions]
            self.db.log_audit_query(
                session_ids=session_ids,
                user_query=user_query,
                final_model=final_model,
                chain_log=" → ".join(chain_log)
            )
        
        return {
            "answer": answer or "All models in chain failed",
            "final_model": final_model,
            "chain_log": chain_log
        }
    
    def _build_context(self, sessions: List[Dict[str, Any]]) -> str:
        """Build context from sessions.
        
        Args:
            sessions: List of session dicts
            
        Returns:
            Combined context string
        """
        if not sessions:
            return "No sessions provided"
        
        if len(sessions) == 1:
            # Single session - use full content
            return self._extract_session_content(sessions[0])
        
        # Multiple sessions - combine with headers
        parts = []
        for i, session in enumerate(sessions, 1):
            header = f"=== Session {i}: {session.get('title', 'Untitled')} ==="
            content = self._extract_session_content(session)
            parts.append(f"{header}\n{content}")
        
        return "\n\n".join(parts)
    
    def _extract_session_content(self, session: Dict[str, Any]) -> str:
        """Extract content from session.
        
        Args:
            session: Session dict
            
        Returns:
            Session content string
        """
        # This would load actual session content from file
        # For now, use summary
        return session.get("summary", "No content")
    
    async def _query_model(
        self,
        model_config: ModelConfig,
        context: str,
        user_query: str
    ) -> str:
        """Query a single model.
        
        Args:
            model_config: Model configuration
            context: Context string
            user_query: User question
            
        Returns:
            Model response text
        """
        # Build prompt
        prompt = self._build_prompt(context, user_query)
        
        # Get API key
        api_key = self._get_api_key(model_config)
        
        # Query using litellm
        import litellm
        
        response = await asyncio.wait_for(
            litellm.acompletion(
                model=f"{model_config.provider}/{model_config.model}",
                messages=[{"role": "user", "content": prompt}],
                api_key=api_key,
                timeout=model_config.timeout,
                temperature=model_config.temperature
            ),
            timeout=model_config.timeout
        )
        
        return response.choices[0].message.content
    
    def _build_prompt(self, context: str, user_query: str) -> str:
        """Build prompt for model.
        
        Args:
            context: Session context
            user_query: User question
            
        Returns:
            Formatted prompt
        """
        return f"""You are analyzing AI agent session logs.

<context>
{context}
</context>

<question>
{user_query}
</question>

Provide a concise, accurate answer based on the session context. If the context doesn't contain enough information, say so."""
    
    def _get_api_key(self, model_config: ModelConfig) -> Optional[str]:
        """Get API key for model.
        
        Args:
            model_config: Model configuration
            
        Returns:
            API key or None
        """
        if model_config.api_key_env:
            return os.environ.get(model_config.api_key_env)
        
        # Default env var names
        env_vars = {
            "google": "GEMINI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
        }
        
        env_var = env_vars.get(model_config.provider)
        if env_var:
            return os.environ.get(env_var)
        
        return None


class AuthError(Exception):
    """Authentication error."""
    pass

class RateLimitError(Exception):
    """Rate limit error."""
    pass
```

## Acceptance Criteria

- [ ] CognitiveRouter class with query() method
- [ ] litellm integration for all providers
- [ ] Prompt template for cross-session queries
- [ ] Token counting before API call
- [ ] Context window per model
- [ ] Multi-session context assembly
- [ ] Error classification (auth/rate-limit/timeout)
- [ ] Unit tests with mock API

## Next Steps

1. Update state.json: set card 17 to "completed"
2. Continue with Card 18 (Fallback Chain)
