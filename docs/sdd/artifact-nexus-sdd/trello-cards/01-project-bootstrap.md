# Card 01: Project Bootstrap

| Field | Value |
|-------|-------|
| **ID** | AN-01 |
| **Story Points** | 2 |
| **Depends On** | None |
| **Sprint** | Phase 1 |

## User Story

> As a developer, I want to initialize the Python project with proper structure so that I can start implementing Artifact Nexus.

## Context

Read before starting:
- [requirements.md](../requirements.md) - Section 6 (Tech Stack)
- [KICKOFF.md](./KICKOFF.md) - Phase 1 overview

## Instructions

### Step 1: Create Project Structure

```bash
cd /home/pets/temp/jsonl_dashboard

# Create directories
mkdir -p src/nexus src/nexus/tui src/nexus/db src/nexus/parser src/nexus/router
mkdir -p tests tests/fixtures
mkdir -p ~/.nexus
```

### Step 2: Initialize Poetry

```bash
cd /home/pets/temp/jsonl_dashboard
poetry init --name "artifact-nexus" --python "^3.10"

# Add dependencies
poetry add textual rapidfuzz pyyaml litellm
poetry add --group pytest pytest pytest-asyncio
poetry add --group dev black mypy ruff
```

### Step 3: Create pyproject.toml Scripts

```toml
[tool.poetry.scripts]
nexus = "nexus.cli:main"

[tool.poetry.dependencies]
python = "^3.10"
textual = "^0.50.0"
rapidfuzz = "^3.6.0"
pyyaml = "^6.0.0"
litellm = "^1.30.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
black = "^24.0.0"
mypy = "^1.8.0"
ruff = "^0.1.0"
```

### Step 4: Create Initial Files

```bash
# Create __init__.py files
touch src/nexus/__init__.py
touch src/nexus/tui/__init__.py
touch src/nexus/db/__init__.py
touch src/nexus/parser/__init__.py
touch src/nexus/router/__init__.py

# Create CLI entry point
touch src/nexus/cli.py

# Create config file
cat > ~/.nexus/config.yaml << 'EOF'
# Artifact Nexus Configuration
language: "ru"
watcher:
  enabled: true
  polling_interval: 30  # seconds
workspaces:
  - ~/.codex/sessions
  - ~/.qwen/projects
  - ~/.kimi/sessions
  - ~/.gemini/tmp
EOF
```

### Step 5: Create Hello World TUI

```python
# src/nexus/cli.py
from textual.app import App

class NexusApp(App):
    """Artifact Nexus - Terminal observability for AI agents."""
    
    def on_mount(self) -> None:
        self.push_screen("main")
    
    def on_key(self, event) -> None:
        if event.key == "q":
            self.exit()

if __name__ == "__main__":
    app = NexusApp()
    app.run()
```

### Step 6: Verify Installation

```bash
# Install dependencies
poetry install

# Run hello world
poetry run python -c "from textual.app import App; print('Textual OK')"

# Test CLI entry point
poetry run nexus --help 2>/dev/null || echo "CLI needs implementation"
```

## Acceptance Criteria

- [ ] Poetry project initialized with Python 3.10+
- [ ] All dependencies installed (textual, rapidfuzz, pyyaml, litellm)
- [ ] Directory structure created (src/nexus/*, tests/*)
- [ ] ~/.nexus/config.yaml exists
- [ ] `poetry install` succeeds
- [ ] Basic Textual import works
- [ ] No lint errors: `poetry run ruff check src/`
- [ ] Type checking passes: `poetry run mypy src/`

## Next Steps

After completing this card:
1. Update state.json: set card 01 to "completed"
2. Read next card: [02-database-schema.md](./02-database-schema.md)
3. Continue execution
