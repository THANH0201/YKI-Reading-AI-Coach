## User Input

> Execute the user's requested full structural rearchitecture in the current repository. User choices are fixed: keep Streamlit as the frontend; add a separate FastAPI backend; provide MCP over Streamable HTTP; migrate all current functionality while preserving behavior. The user is learning and wants folder names / README to make technologies and the runtime flow obvious; design for future identity/auth, billing, and additional modules without modifying unrelated modules.
>
> Architecture target (adapt only when source evidence requires): apps/web (Streamlit UI and HTTP API client only), apps/api (FastAPI REST/BFF), apps/mcp-server (MCP server / Streamable HTTP tools), packages/contracts (versioned request/response schemas), backend/modules/{reading,writing,tutor,exam_library,identity,billing} with extensible module entrypoints and explicit api/application/domain/infrastructure boundaries where justified; backend/platform for dependency wiring/policies/events; infrastructure adapters for SQLite and external Groq LLM. Implement identity/billing as disabled extension points only, not pretend auth/payment is already functional. Both REST and MCP adapters must call the same application use cases; host must not import repositories/database/LLM/business modules directly. Keep Streamlit frontend functionally equivalent and use stable contracts. Preserve legal/consent behavior and all existing current features (reading analysis, exam sample library/ingestion, timer/scoring, tutor, writing analysis). Do not build fake Listening/Speaking functions; retain clear placeholders if currently present.
>
> Scope is implementation, not just advice: create/move/refactor code and update tests, dependencies, README with exact startup commands and a clear folder map/flow. Add unit/contract tests for tool/API schemas and end-to-end local startup where feasible. Do not change unrelated functionality. Before editing, account for the dirty worktree: many project files are untracked/modified from prior user work. Integrate and preserve these changes; never revert them. NEVER read, copy, print, or edit `.env`; do not modify `data/yki.db` or other user data. Do not commit. Do not use destructive git operations. Use a migration strategy that keeps a working runnable app; avoid importing removed legacy paths or provide minimal compatibility shims only if needed. If exact transport/library APIs are uncertain, inspect installed/dependency documentation and verify with tests rather than guessing.
>
> The full suite baseline before your changes: 123 passed, 2 failed (pre-existing: tests/test_article_ingestion.py::test_crawl_imports_eligible_full_text_and_skips_duplicate and tests/test_tutor.py::test_tutor_saves_lemma_and_inflection_from_grammar_answer). Keep these unrelated failures isolated; report them. Stop when the restructured app is runnable, relevant tests pass, and README explains the layout/runtime flow. Return an exact summary of files/modules moved or created, architecture/runtime flow, tests run and results, remaining risks or limitations.
>
> Continue now; the user already answered the architecture choices directly in the parent session: Streamlit frontend, FastAPI backend, MCP Streamable HTTP, migrate all existing features. There is no pending clarification—do not wait for a form or ask the user again. Implement this in the repository as bounded in your original task. Preserve dirty worktree, do not inspect/edit .env or modify data/yki.db, do not commit. Aim to deliver a runnable migrated application and report concrete changes/tests; proceed without further clarification.

**Project started**: 2026-11-08T14:00:16Z

## Tasks

### Phase: Project Guardrails
- ✅ t1 [teamlead] Define migration constitution and behavior-preservation guardrails (14:21Z→14:25Z, 3m 12s)

### Phase: Discovery
- 🔄 t2 [architect] Analyze current architecture, entrypoints, dependencies, and migration risks (retry dispatched 14:46Z) [deps: t1, t2.1]
- ✅ t3 [pm] Inventory existing user-facing features and behavior for parity (14:26Z→14:30Z, 4m 04s) [deps: t1]
- ✅ t2.1 [architect] Resolve and document mitigations for HIGH migration risks found in t2 (14:38Z→14:44Z, 5m 26s) [deps: t2, t3]

### Phase: Target Design
- ⏳ t4 [architect] Design module boundaries, shared use cases, REST/MCP contracts, and migration strategy [deps: t2, t3]

### Phase: Data and Test Design
- ⏳ t5 [dba] Define SQLite adapter and data-preservation strategy [deps: t2, t3, t4]
- ⏳ t6 [teamlead] Define test strategy for contracts, parity, and local startup [deps: t2, t3]

### Phase: Implementation Plan
- ⏳ t7 [teamlead] Plan sequenced implementation and task breakdown [deps: t4, t5, t6]
- ⏳ t8 [teamlead] Quality-gate implementation plan and traceability [deps: t7]

⏳ [Execute + Validate phases — pending deep planning completion]
