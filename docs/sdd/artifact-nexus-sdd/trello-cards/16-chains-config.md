# Card 16: chains.yaml Parser

| Field | Value |
|-------|-------|
| **ID** | AN-16 |
| **Story Points** | 2 |
| **Depends On** | AN-01 |
| **Sprint** | Phase 3 |

## User Story

> As a system, I want to load and validate Cognitive Router chain configuration so that fallback chains can be used for AI queries.

## Context

- [requirements.md](../requirements.md) - Section 5.2 (Configuration)

## Instructions

### Step 1: Create ChainsConfig Class

```python
# src/nexus/router/chains_config.py
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for a single model in the chain."""
    name: str
    provider: str
    model: str
    timeout: int = 30  # seconds
    context_limit: int = 128000
    temperature: float = 0.2
    trigger_condition: str = "on_failure"  # on_failure | on_uncertainty
    api_key_env: Optional[str] = None
    base_url: Optional[str] = None

@dataclass
class ChainConfig:
    """Configuration for a fallback chain."""
    name: str
    models: List[ModelConfig]

class ChainsConfig:
    """Loads and validates chains.yaml configuration."""
    
    DEFAULT_PATH = Path.home() / ".nexus" / "chains.yaml"
    
    DEFAULT_CHAIN = {
        "default": [
            {
                "name": "fast_triage",
                "provider": "ollama",
                "model": "qwen2.5-coder:32b",
                "timeout": 15,
                "context_limit": 32000
            },
            {
                "name": "deep_analysis",
                "provider": "google",
                "model": "gemini-1.5-pro-latest",
                "timeout": 60,
                "context_limit": 2000000
            }
        ]
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize chains config.
        
        Args:
            config_path: Path to chains.yaml (default: ~/.nexus/chains.yaml)
        """
        self.config_path = config_path or self.DEFAULT_PATH
        self.chains: Dict[str, ChainConfig] = {}
        self._load()
    
    def _load(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            # Use default chain
            self._parse_chains(self.DEFAULT_CHAIN)
            return
        
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            
            self._parse_chains(config or {})
        
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {self.config_path}: {e}")
        except Exception as e:
            # Use default on error
            self._parse_chains(self.DEFAULT_CHAIN)
    
    def _parse_chains(self, config: Dict[str, Any]) -> None:
        """Parse chains from config dict.
        
        Args:
            config: Config dict with 'chains' key
        """
        chains_data = config.get("chains", config)
        
        for chain_name, models in chains_data.items():
            if not isinstance(models, list):
                continue
            
            model_configs = []
            for model_data in models:
                model_config = ModelConfig(
                    name=model_data.get("name", "unknown"),
                    provider=model_data.get("provider", "unknown"),
                    model=model_data.get("model", "unknown"),
                    timeout=model_data.get("timeout", 30),
                    context_limit=model_data.get("context_limit", 128000),
                    temperature=model_data.get("temperature", 0.2),
                    trigger_condition=model_data.get("trigger_condition", "on_failure"),
                    api_key_env=model_data.get("api_key_env"),
                    base_url=model_data.get("base_url")
                )
                model_configs.append(model_config)
            
            self.chains[chain_name] = ChainConfig(
                name=chain_name,
                models=model_configs
            )
    
    def get_chain(self, chain_name: str = "default") -> ChainConfig:
        """Get chain configuration.
        
        Args:
            chain_name: Name of chain to get
            
        Returns:
            ChainConfig object
        """
        if chain_name in self.chains:
            return self.chains[chain_name]
        
        # Fallback to default
        if "default" in self.chains:
            return self.chains["default"]
        
        # Create empty chain
        return ChainConfig(name=chain_name, models=[])
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self.chains.clear()
        self._load()
    
    def validate(self) -> List[str]:
        """Validate configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        for chain_name, chain in self.chains.items():
            if not chain.models:
                errors.append(f"Chain '{chain_name}' has no models")
            
            for i, model in enumerate(chain.models):
                if not model.provider:
                    errors.append(f"Chain '{chain_name}' model {i}: missing provider")
                if not model.model:
                    errors.append(f"Chain '{chain_name}' model {i}: missing model")
        
        return errors
```

### Step 2: Create Example Config

```yaml
# ~/.nexus/chains.yaml
chains:
  default:
    # Step 1: Fast & Cheap (Local)
    - name: "fast_triage"
      provider: "ollama"
      model: "qwen2.5-coder:32b"
      timeout: 15
      context_limit: 32000
    
    # Step 2: High Context (Cloud)
    - name: "deep_analysis"
      provider: "google"
      model: "gemini-1.5-pro-latest"
      temperature: 0.2
      context_limit: 2000000
      trigger_condition: "on_failure"
    
    # Step 3: Fallback (Anthropic)
    - name: "final_fallback"
      provider: "anthropic"
      model: "claude-3-5-sonnet-20241022"
      timeout: 60
      context_limit: 200000

  offline:
    # Local-only chain
    - name: "local_only"
      provider: "ollama"
      model: "llama3.1:8b"
      timeout: 30
      context_limit: 8000
```

## Acceptance Criteria

- [ ] ChainsConfig class
- [ ] Load from ~/.nexus/chains.yaml
- [ ] Validation schema
- [ ] Default chain if file missing
- [ ] All fields documented
- [ ] Error on invalid YAML
- [ ] Hot reload option

## Next Steps

1. Update state.json: set card 16 to "completed"
2. Continue with Card 17 (CognitiveRouter)
