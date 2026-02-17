# Card 18: Fallback Chain Logic

| Field | Value |
|-------|-------|
| **ID** | AN-18 |
| **Story Points** | 3 |
| **Depends On** | AN-17 (CognitiveRouter) |
| **Sprint** | Phase 3 |

## User Story

> As a system, I want intelligent fallback with circuit breaker pattern so that failed models don't block subsequent queries.

## Context

- [requirements.md](../requirements.md) - Section 5.1 (Fallback Logic)

## Instructions

### Step 1: Create CircuitBreaker Class

```python
# src/nexus/router/circuit_breaker.py
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

class CircuitBreaker:
    """Circuit breaker for model fallback."""
    
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 300,  # 5 minutes
        half_open_requests: int = 1
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            half_open_requests: Requests allowed in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        
        self._failures: Dict[str, int] = {}
        self._last_failure: Dict[str, datetime] = {}
        self._state: Dict[str, str] = {}  # closed, open, half-open
        self._half_open_requests: Dict[str, int] = {}
    
    def can_execute(self, model_name: str) -> bool:
        """Check if model can be executed.
        
        Args:
            model_name: Model identifier
            
        Returns:
            True if execution allowed
        """
        state = self._state.get(model_name, "closed")
        
        if state == "closed":
            return True
        
        if state == "open":
            # Check if recovery timeout passed
            last_failure = self._last_failure.get(model_name)
            if last_failure:
                elapsed = (datetime.now() - last_failure).total_seconds()
                if elapsed >= self.recovery_timeout:
                    # Transition to half-open
                    self._state[model_name] = "half-open"
                    self._half_open_requests[model_name] = self.half_open_requests
                    return True
            return False
        
        if state == "half-open":
            # Allow limited requests
            remaining = self._half_open_requests.get(model_name, 0)
            return remaining > 0
        
        return True
    
    def record_success(self, model_name: str) -> None:
        """Record successful execution.
        
        Args:
            model_name: Model identifier
        """
        self._failures[model_name] = 0
        self._state[model_name] = "closed"
        self._half_open_requests.pop(model_name, None)
    
    def record_failure(self, model_name: str, error: Exception) -> None:
        """Record failed execution.
        
        Args:
            model_name: Model identifier
            error: Exception that occurred
        """
        self._failures[model_name] = self._failures.get(model_name, 0) + 1
        self._last_failure[model_name] = datetime.now()
        
        # Check if we should open circuit
        if self._failures[model_name] >= self.failure_threshold:
            self._state[model_name] = "open"
        
        # Decrement half-open counter
        if self._state.get(model_name) == "half-open":
            self._half_open_requests[model_name] -= 1
            if self._half_open_requests[model_name] <= 0:
                # Back to open if still failing
                self._state[model_name] = "open"
    
    def get_status(self, model_name: str) -> Dict[str, Any]:
        """Get circuit breaker status.
        
        Args:
            model_name: Model identifier
            
        Returns:
            Status dict
        """
        return {
            "state": self._state.get(model_name, "closed"),
            "failures": self._failures.get(model_name, 0),
            "last_failure": self._last_failure.get(model_name),
        }
```

### Step 2: Update CognitiveRouter with Circuit Breaker

```python
# src/nexus/router/cognitive_router.py (update)
from .circuit_breaker import CircuitBreaker

class CognitiveRouter:
    """AI chat engine with fallback chain."""
    
    def __init__(self, chains_config: ChainsConfig, db_manager=None):
        super().__init__()
        self.config = chains_config
        self.db = db_manager
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=300  # 5 minutes
        )
    
    async def query(
        self,
        sessions: List[Dict[str, Any]],
        user_query: str,
        chain_name: str = "default"
    ) -> Dict[str, Any]:
        """Query sessions with fallback chain."""
        chain = self.config.get_chain(chain_name)
        
        chain_log = []
        final_model = None
        answer = None
        
        context = self._build_context(sessions)
        
        for model_config in chain.models:
            # Check circuit breaker
            if not self.circuit_breaker.can_execute(model_config.name):
                chain_log.append(f"{model_config.name}: circuit open (skipped)")
                continue
            
            try:
                answer = await self._query_model(
                    model_config=model_config,
                    context=context,
                    user_query=user_query
                )
                
                final_model = model_config.name
                chain_log.append(f"{model_config.name}: success")
                
                # Record success
                self.circuit_breaker.record_success(model_config.name)
                break
            
            except AuthError as e:
                chain_log.append(f"{model_config.name}: auth failed")
                self.circuit_breaker.record_failure(model_config.name, e)
                # Don't retry auth failures
                continue
            
            except RateLimitError as e:
                chain_log.append(f"{model_config.name}: rate limited")
                self.circuit_breaker.record_failure(model_config.name, e)
                continue
            
            except TimeoutError as e:
                chain_log.append(f"{model_config.name}: timeout")
                self.circuit_breaker.record_failure(model_config.name, e)
                continue
            
            except Exception as e:
                chain_log.append(f"{model_config.name}: failed ({e})")
                self.circuit_breaker.record_failure(model_config.name, e)
                continue
        
        return {
            "answer": answer or "All models in chain failed",
            "final_model": final_model,
            "chain_log": chain_log
        }
```

## Acceptance Criteria

- [ ] CircuitBreaker class
- [ ] Failure threshold (N failures in M minutes)
- [ ] Recovery timeout
- [ ] Half-open state
- [ ] Exponential backoff option
- [ ] Failed model cache
- [ ] User notification on degraded mode
- [ ] Integrated with CognitiveRouter

## Next Steps

1. Update state.json: set card 18 to "completed"
2. Continue with Card 19 (Chat UI)
