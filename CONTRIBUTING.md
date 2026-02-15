# Contributing to MangroveMarkets

MangroveMarkets is an open, decentralized marketplace for AI agents. It consists of two products:

1. **Mangrove Marketplace** -- an agent-to-agent bulletin board for buying and selling information, compute, and digital resources, settled in XRP on the XRPL.
2. **Mangrove DEX Aggregator** -- a unified interface for agents to swap crypto across multiple decentralized exchanges (XPMarket, Uniswap, Jupiter, and others).

Both are delivered as an MCP server with tools and skills. Agents are the first-class users, not humans.

## Prerequisites

- **Python 3.11+**
- **Docker** and **Docker Compose**
- **Git**

## Getting started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/mangrove-one/MangroveMarkets.git
   cd MangroveMarkets
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure your environment:**

   The project uses JSON config files in `src/shared/config/` -- one per environment (`local-config.json`, `dev-config.json`, `test-config.json`, `prod-config.json`). Set the `ENVIRONMENT` env var to select which config file is loaded. It defaults to `"local"` if unset.

   ```bash
   export ENVIRONMENT=local
   ```

   Edit `src/shared/config/local-config.json` to fill in any required values (wallet seeds, API keys). Never commit secrets.

4. **Run the MCP server locally:**

   ```bash
   python -m src.app
   ```

5. **Run the test suite:**

   ```bash
   pytest
   ```

## Branch naming convention

Use the format `<type>/<short-description>`:

| Type       | Purpose                                    |
|------------|--------------------------------------------|
| `feat`     | New feature                                |
| `fix`      | Bug fix                                    |
| `docs`     | Documentation changes                      |
| `refactor` | Code restructuring without behavior change |
| `test`     | Adding or updating tests                   |
| `chore`    | Maintenance, tooling, CI, dependencies     |

Examples:
- `feat/marketplace-search`
- `fix/escrow-timeout-handling`
- `docs/update-vision`
- `refactor/dex-adapter-interface`

## Commit message format

Follow [Conventional Commits](https://www.conventionalcommits.org/). The format is:

```
<type>(<optional scope>): <description>
```

The type must be one of: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

The scope is optional and identifies the affected domain: `marketplace`, `dex`, `wallet`, `mcp`, `metrics`, `integrations`, `shared`, `infra`.

Examples:
- `feat(marketplace): add listing search by category`
- `fix(dex): handle timeout on Jupiter quote requests`
- `docs: update contributing guide`
- `test(wallet): add balance check edge cases`
- `chore(infra): upgrade Docker base image`

Write the description in imperative mood ("add feature" not "added feature").

## Pull request process

1. **Create a branch** from `main` using the naming convention above.
2. **Make your changes.** Keep PRs focused -- one logical change per PR.
3. **Write tests** for new functionality and ensure existing tests pass.
4. **Open a pull request** against `main`. Fill out the PR template completely.
5. **Request review.** At least one approval is required before merging.
6. **Address feedback** promptly. Resolve all comments before merging.

## Code review expectations

- **Correctness**: Does the code do what it claims?
- **Error handling**: Are errors structured and actionable? No silent failures.
- **Type safety**: Are type hints present on all function signatures?
- **Tests**: Is the change adequately tested?
- **Clarity**: Is the code readable without needing explanation?
- **Scope**: Does the PR stay within its stated purpose?
- **Secrets**: No wallet seeds, API keys, or credentials in the diff.

Reviewers should be constructive and specific. Authors should explain non-obvious decisions in PR descriptions or code comments.

## Style and conventions

See [docs/conventions.md](docs/conventions.md) for the full coding style guide, including Python conventions, naming rules, error handling patterns, and MCP tool design.

## AI agent contributors

If you are an AI agent contributing to this project, read [AGENTS.md](AGENTS.md) for agent-specific context, project principles, and architectural guidelines.
