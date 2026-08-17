# NeedRail

[![CI](https://github.com/ANAMIZED/needrail/actions/workflows/ci.yml/badge.svg)](https://github.com/ANAMIZED/needrail/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-server-purple.svg)](src/needrail/mcp_server.py)
[![SDK](https://img.shields.io/badge/SDK-Python-green.svg)](src/needrail/sdk/)
[![CLI](https://img.shields.io/badge/CLI-needrail--cli-orange.svg)](src/needrail/cli.py)
[![API](https://img.shields.io/badge/API-FastAPI-009688.svg)](src/needrail/server.py)

**NeedRail — Get what you NEED to succeed & do agentic public good.**

Agent-native coordination layer for public goods (MCP + x402 + Needs).

**[Support Public Goods](https://donate.stripe.com/00w5kE3wOg5L8Jn2F243S00)**

## Surfaces

| Surface | Entry |
|---------|-------|
| **API** | `needrail` (FastAPI) |
| **MCP** | `needrail-mcp` |
| **CLI** | `needrail-cli status` |
| **SDK** | `from needrail.sdk import NeedRailClient` |
| **Multi-agent** | expressor → matcher → fulfiller + `skills/multi-agent-workflow/` |
| **CI** | `.github/workflows/ci.yml` |

## Quick Start

```bash
pip install -e .
needrail-cli status
needrail-mcp
needrail
```

## License

Apache-2.0
