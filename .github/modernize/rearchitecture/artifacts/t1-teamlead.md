<!--
Sync Impact Report
- Version change: no prior constitution -> 1.0.0 (initial constitution for this rearchitecture)
- Modified principles: N/A; initial principles are Behavior Preservation, Explicit Boundaries,
  Shared Application Use Cases, Protected Data and Consent, and Verifiable Incremental Migration.
- Added sections: migration mode, target technology stack, architectural invariants, delivery and
  verification, governance, upstream-artifact traceability.
- Removed sections: none.
- Templates: creating-implementation-plan/templates/plan-template.md — checked; no edit required;
  feature-inventory/templates/spec-template.md — checked; no edit required;
  creating-implementation-plan/templates/tasks-template.md — checked; no edit required.
- Deferred TODOs: none. Exact FastAPI/MCP versions remain an implementation-time compatibility
  check, not an unresolved architectural choice. Initial ratification date is this adoption date.
-->

# YKI Reading AI Coach Constitution

## Migration Mode

**Mode**: REWRITE

**Justification**: Replace the monolithic application structure with independently
owned modules and Streamlit, REST, and MCP adapters while retaining the existing
product and its observable behavior. Migrate incrementally and keep the application
runnable; this is not permission to discard or redesign existing behavior.

## Core Principles

### I. Behavior Preservation Is the Acceptance Baseline

Every existing user-facing capability and observable rule MUST remain available
unless the user explicitly changes scope. Preserve legal notices, consent and
article eligibility rules; reading analysis and question format; exam library
ingestion, duplicate handling, timer, scoring and result behavior; tutor behavior;
writing analysis; and current data/session persistence semantics. Do not invent
Listening or Speaking functionality: retain and clearly label existing
placeholders. Preserve unrelated work and user changes. Any source-backed
behavior change requires an explicit rationale, corresponding tests, and an
approved scope decision.

### II. Enforce Module Ownership and Adapter Boundaries

The target structure MUST make technology and runtime responsibilities evident:
`apps/web` contains only the Streamlit UI and HTTP API client; `apps/api` hosts
FastAPI REST/BFF endpoints; `apps/mcp-server` hosts MCP tools over Streamable
HTTP; `packages/contracts` holds versioned schemas; `backend/modules/` owns
reading, writing, tutor, exam_library, identity, and billing; and
`backend/platform` owns composition and cross-cutting policies/events.
Infrastructure adapters own SQLite and Groq integration.

Business capabilities MUST be owned by their module, not duplicated in a host.
Module entrypoints MUST be explicit and extensible. Use `api`, `application`,
`domain`, and `infrastructure` boundaries where they clarify real responsibility;
do not add empty or ceremonial layers. Application code depends on abstractions
for storage and external model access, while concrete adapters implement them.
Composition roots wire dependencies. Hosts MUST NOT import repositories,
database implementations, LLM clients, or business internals directly.

### III. REST and MCP Reuse the Same Application Use Cases

FastAPI and MCP are transport adapters, not separate business implementations.
Both MUST invoke the same application use cases and enforce the same validation,
authorization policy (where enabled), and error semantics. API and MCP inputs and
outputs MUST be represented by stable, versioned contracts in
`packages/contracts`; contract changes require compatibility review and contract
tests. The Streamlit UI MUST communicate with application features through its
HTTP client, not direct imports of backend modules or persistence code.

### IV. Protect Existing Data, Consent, and Secrets

Migration MUST preserve the existing SQLite database and user data. Do not edit,
replace, reset, or migrate `data/yki.db` or other user data as part of routine
development or tests; use isolated temporary databases and reversible,
user-approved migration procedures when a schema change is necessary. Preserve
the distinction between approved library content and transient user-submitted
content. Consent decisions and legal safeguards MUST remain effective across
the new transports. Never inspect, print, copy, or edit `.env`; keep credentials
out of source, tests, logs, contracts, and artifacts, and access configuration
only through runtime configuration interfaces.

Identity and billing are disabled extension points only: their modules may expose
clear registration/configuration seams, but MUST NOT claim to authenticate,
authorize users, take payment, or simulate those capabilities. Do not weaken
existing safeguards to make a route or demo appear functional.

### V. Migrate in Verifiable, Runnable Increments

Before removing or relocating an existing path, provide its replacement and
verify behavior; retain only minimal, documented compatibility shims where
callers still require them. Keep a runnable application at each practical
migration checkpoint. Tests MUST cover the migrated behavior and boundaries:
unit tests for use cases, contract/schema tests for REST and MCP, integration
tests for adapters and persistence, and a local startup/user-journey test where
feasible. Tests MUST use isolated state and MUST NOT mutate user data.

The supplied baseline is 123 passing tests plus two pre-existing failures:
`tests/test_article_ingestion.py::test_crawl_imports_eligible_full_text_and_skips_duplicate`
and `tests/test_tutor.py::test_tutor_saves_lemma_and_inflection_from_grammar_answer`.
Keep those failures distinguished from regressions, report actual outcomes, and
do not broaden changes merely to hide or reclassify them. A migration is accepted
only when relevant tests pass, the application starts, contracts are checked,
and any remaining baseline failures or limitations are explicit.

## Target Technology Stack

| Component | Target Version | Notes |
|-----------|---------------|-------|
| Language/runtime | Existing Python runtime | Preserve current runtime compatibility; establish exact supported version during discovery. |
| Frontend | Streamlit 1.66.1 (current declared version) | Retain Streamlit; do not replace it with a new frontend framework. |
| REST backend | FastAPI | Select a compatible version during implementation and verify package/API compatibility. |
| MCP | MCP over Streamable HTTP | Select an SDK version that supports the required transport; verify against current official documentation/package metadata. |
| Contracts | Versioned schemas | Keep transport contracts in `packages/contracts`; schema representation is a design-phase decision. |
| Persistence | SQLite | Preserve existing data and semantics; test against isolated temporary databases. |
| LLM integration | Groq | Keep behind an infrastructure adapter; do not expose credentials or vendor clients to hosts. |
| Dependency management | Existing Python requirements workflow | Add only necessary dependencies and document reproducible installation/startup. |

## Architectural Invariants

- Runtime flows are `Streamlit UI → HTTP API client → FastAPI REST/BFF` and
  `MCP client → MCP Streamable HTTP adapter`; both adapters invoke the same
  application use case, which reaches module-owned logic and platform-wired
  infrastructure adapters (SQLite/Groq).
- REST and MCP adapters use the same application services; neither may contain
  a parallel implementation of business rules.
- `apps/web` remains a client-only presentation boundary. `apps/api` and
  `apps/mcp-server` own transport concerns; dependency composition belongs in
  `backend/platform`.
- New module code belongs to its owning business module. Cross-module behavior
  must be expressed through deliberate application interfaces/contracts, not
  imports of another module's repositories or private implementation.
- README and folder names MUST explain the technology and the runtime flow to a
  learner. Startup commands and configuration requirements must be explicit.
- Version choices not fixed above MUST be verified for runtime compatibility
  before implementation; do not silently substitute a different framework or
  transport.

## Delivery and Verification

For each migration slice, identify the preserved behavior, owning module,
contracts/adapters affected, and tests that demonstrate parity. Prefer vertical
feature slices over moving an entire technical layer without a runnable path.
Update dependency manifests, tests, and README alongside implementation.

The final verification report MUST enumerate changed/moved files and modules,
explain runtime flow, give exact test/startup commands and pass/fail counts,
separate the two stated baseline failures from new regressions, and disclose
remaining risks. Preserve the dirty worktree; do not commit, use destructive Git
operations, or revert unrelated user changes.

## Governance

This constitution governs implementation, tests, and supporting documentation
for the rearchitecture. Amendments require a written reason, impact on behavior
or module boundaries, and review by the coordinator before downstream work
relies on the changed rule. Version changes follow semantic versioning:
MAJOR for incompatible principle changes or removals, MINOR for new principles
or materially expanded requirements, and PATCH for non-semantic clarification.
Every implementation task and final review MUST check compliance. A constitution
violation is CRITICAL and blocks acceptance until corrected or the constitution
is formally amended.

**Version**: 1.0.0 | **Ratified**: 2026-11-08 | **Last Amended**: 2026-11-08

## Upstream Artifacts Consumed

- `.github/modernize/rearchitecture/clarification.md` — fixed choices, defaults,
  data-protection constraints, and known test baseline.
- `.github/modernize/rearchitecture/board.md` — canonical user request, target
  structure, and run constraints.
- `README.md` and `requirements.txt` — documented behavior/context and currently
  declared Python dependencies; no source files or `.env` were inspected.
- `skills/setting-up-constitution/templates/constitution-template.md` — required
  constitution structure and migration-mode fields.

## Evidence Mapping

- `clarification.md#Backend` and `clarification.md#Generic` → Core Principles I,
  III–V and the fixed REST/MCP/data/identity constraints above.
- `board.md#Tasks` / target-architecture request → Core Principles II–III and
  Architectural Invariants: application modules, adapters, contracts, and
  shared use cases.
- `clarification.md#Generic` → Core Principle V: 123-pass / 2-known-failure
  baseline and no user-data mutation.
- `README.md` project summary and `requirements.txt` → Target Technology Stack
  and explicit runtime compatibility verification.

## Template Consistency Review

- `creating-implementation-plan/templates/plan-template.md` — reviewed; its
  Constitution Check supports principle-by-principle verification. No template
  change required.
- `feature-inventory/templates/spec-template.md` — reviewed; requirements and
  acceptance scenarios can record parity and prohibited fake capabilities. No
  template change required.
- `creating-implementation-plan/templates/tasks-template.md` — reviewed; its
  sample says tests are optional, but this request explicitly requires tests,
  so downstream task breakdown MUST include the requested contract and startup
  validation. No template change required.
