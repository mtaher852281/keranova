# Project context

Read README.md for the KeraNova research objective, completed protocol package, public dataset limits and remaining work. The institutional model remains untrained; KeraNova_Fast_Model contains a separate exploratory public CXL experiment. No clinical results should be invented. Keep the institutional protocol separate from the public experiment. Preserve patient grouping and training-fold-only preprocessing.

The owner explicitly requested publication of the entire existing project folder, including dataset.csv, original documents and backups. The earlier publication allowlist was removed. Git internals, the rebuildable graph cache and credential-file patterns remain excluded. Never add credentials or newly obtained identifiable clinical records. Keep protocol_sources, the two published DOCX locations and the committee ZIP synchronized after reviewed revisions; the current committee snapshot predates the exploratory model outputs.

# Global Codex Instructions

## IMPORTANT: Always Use code-review-graph Before Reading Files

**ALWAYS** use the `code-review-graph` MCP tools before reading files or analyzing code changes in ANY project. This saves ~8x tokens.

### Rules (no exceptions):

1. **Before reading multiple files** — use `mcp__code_review_graph__*` tools (blast-radius, impact analysis, semantic search) to scope what actually needs to be read.
2. **Before reviewing code changes** — query the graph first to find impacted nodes instead of reading files blindly.
3. **If the MCP tools are unavailable** — run `code-review-graph build` to rebuild the graph, then retry.
4. **Install per project** — if `.mcp.json` doesn't exist in a new project, run `code-review-graph install` then `code-review-graph build`.

### Why this matters:

The user explicitly requires this to conserve tokens. The tool maps codebase structure using Tree-sitter and identifies blast radius of changes — so targeted reads replace broad file sweeps.
