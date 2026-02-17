---
name: tool-spec
description: Draft an MCP tool specification for a new MangroveMarkets tool
disable-model-invocation: true
argument-hint: "[tool name and purpose]"
---

Draft an MCP tool specification for: $ARGUMENTS

Follow the rules in `.claude/rules/mcp-tools.md` for naming, structure, and error handling.

The spec should include:
1. **Tool name** (with correct prefix: marketplace_, dex_, wallet_, integration_, metrics_)
2. **Description** — one clear sentence
3. **Input parameters** — name, type, required/optional, description
4. **Output schema** — JSON structure returned on success
5. **Error schema** — JSON structure returned on failure (with error, code, message, suggestion)
6. **Example** — one example input and expected output

Output the spec as a JSON schema that could be used in an MCP server tool definition.

Do NOT create any files. Just output the spec for review.
