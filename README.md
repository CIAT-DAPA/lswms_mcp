# Waterpoint monitoring MCP Server


MCP server exposing the [Waterpoint API v1](https://webapi.waterpointsmonitoring.net/) 
to the AI ​​ecosystem. It allows agents to reason about historical 
 data, waterpoint status, and recommendations directly from a conversation.

## 🏷️ Version & Tags

**Current version:** `v0.1.0`  
**Tags:** `waterpoints`, `mcp`, `python`, `agent-ai`, `climate`

---
## Architecture

```
AI Clients (Bot)
        │  MCP Protocol (SSE / Streamable)
        ▼
Waterpoint MCP Server  ←── FastMCP
        │
Waterpoint API v1  ←── webapi.waterpointsmonitoring.net (FastAPI)
        │
MongoDB + GeoServer
```
## Resources

## Installation

### Requirements
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recomendado) o pip

### Setup

```bash
# Clone repository
git clone https://github.com/CIAT-DAPA/lswms_mcp.git
cd lswms_mcp

# Install dependencies
# NOt active the venv manually: uv creates and manage.
# In Windows, has the venv activate stock .venv\Scripts\ and uv sync fail
# with "Access is denied (os error 5)" to try to create.
uv python install 3.10   # Just if you don't have Python 3.10
uv sync

# Configure env
cp .env.example .env

# Start server
uv run lswms-mcp
```

## Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|

## Project structured

```
lswms_mcp/
├── src/                        # Source code
│   ├── lswms_mcp/           # MCP Server
│   │   ├── __init__.py
│   │   ├── prompts.py          # Prompts MCP
│   │   ├── resources.py        # Resources MCP
│   │   ├── server.py           # Run the server for MCP
│   │   ├── settings.py         # Settings via Environmental variables
│   └───└── tools.py            # Tools MCP
├── tests/
│   ├── 
│   └── 
├── pyproject.toml
├── 
├── Jenkinsfile
├── .env.example
└── README.md
```

## Development

```bash
# Tests con cobertura
uv run pytest -v
uv run pytest -v --tb=short

# Linting
uv run ruff check .

# Dev
mcp dev "./src/lswms_mcp/server.py"

```
