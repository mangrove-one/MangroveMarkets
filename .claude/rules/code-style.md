# Code Style Rules

## General

- Write clean, readable code. No clever tricks.
- Meaningful variable and function names — agents will read error messages, so make them descriptive.
- Comment the "why", not the "what".
- Prefer simplicity over abstraction. Don't create an interface until you need two implementations.

## File Naming

- Lowercase with hyphens for files: `marketplace-search.ts`, `dex-adapter.ts`
- No all-caps markdown files except `README.md` and `AGENTS.md`
- Test files mirror source: `src/marketplace/listing.ts` → `tests/marketplace/listing.test.ts`

## Error Handling

- Every MCP tool must return structured errors that an agent can parse and act on
- No silent failures — if something goes wrong, say what and why
- Include actionable context: "Insufficient XRP balance: have 5, need 10" not "Transaction failed"

## Dependencies

- Minimize external dependencies
- Prefer well-maintained, widely-used packages
- Pin versions in package.json
