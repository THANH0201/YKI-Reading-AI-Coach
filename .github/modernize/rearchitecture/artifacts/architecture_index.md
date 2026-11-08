# Architecture Index — Current-State Discovery

This index is not the full contract. Do not implement from this file alone; follow the artifact paths below.

## Implementation Guide

This guide indexes **current-state discovery units**, not a committed target-unit count. The target module and adapter design belongs to t4. Implementation scope is controlled by `t2-architect-migration-boundary.yaml::must_rewrite`; source anchors prove current behavior exists and are not, by themselves, a file-move checklist.

### Global artifacts

- `t2-architect-unit-graph.yaml`
  - Who reads: all design and implementation workers.
  - Use for: current external triggers, source anchors, shared references and dependencies.
  - How to consume: find your assigned current unit; follow its anchors and `shared_refs`. Do not infer the target module count from this graph.
- `t2-architect-migration-boundary.yaml`
  - Who reads: all implementation workers.
  - Use for: the phased runtime boundary and implementation scope.
  - How to consume: use `must_rewrite` and `copy_as_is`; preserve `legacy_allowed_to_remain` unless cleanup is explicitly approved. `source_anchors` are not rewrite targets.
- `t2-architect-wire-contracts.yaml`
  - Who reads: workers implementing provider, feed, or persistence adapters and future transport contracts.
  - Use for: current external SDK/HTTP and storage behavior.
  - How to consume: filter by `unit`; retain provider-specific behavior. No pre-existing REST or MCP contract is present.
- `t2-architect-shared-modules.yaml`
  - Who reads: workers touching shared current code.
  - Use for: shared utilities, records, persistence and provider references.
  - How to consume: filter by `used_by_units`; for each unit, only rely on the `shared_refs[].used_fields` allowlist in the unit graph.
- `t2-architect-cross-unit-state.yaml`
  - Who reads: workers defining the new HTTP/session boundary.
  - Use for: state that crosses current unit boundaries, plus the note describing state currently confined to the Streamlit page.
  - How to consume: filter `flows` by `writer.unit` or `reader.unit`; then read the note for page-local exam/tutor state that must become an explicit target contract.
- `t2-architect-architecture.md`
  - Who reads: design and implementation workers.
  - Use for: current dependency direction, runtime shape, feature placement and migration risks.
  - How to consume: treat risks as source-backed constraints; use t2.1 for the already-agreed mitigation decisions.
- `t2-architect-project-structure.md`, `t2-architect-tech-stack.md`, and `t2-architect-data-model.md`
  - Who reads: all workers needing package, runtime/dependency, or persisted-schema context.
  - Use for: current packages and entrypoints, declared dependencies, and SQLite schema/relationships.
  - How to consume: these record the existing system only; do not treat them as target design or permission to access `data/yki.db`.
- `t2.1-architect.md`
  - Who reads: design and implementation workers.
  - Use for: agreed mitigations for the seven HIGH risks identified by t2.
  - How to consume: preserve its controls and acceptance evidence; it does not claim the risks are closed in code.

### Unit: `streamlit-home`

- External trigger: Streamlit script `app.py`, with all current page sections and exam/tutor interactions.
- Must read:
  - `units/streamlit-home/behavior.yaml` — side effects, branches, error semantics and persistence boundary.
  - `units/streamlit-home/bindings.yaml` — Streamlit startup, fragment, session state and runtime configuration.
  - `units/streamlit-home/unit_decomposition.yaml` — advisory split candidates only; `commit: false`.
- Relevant global rows:
  - `t2-architect-wire-contracts.yaml`: rows with `unit: streamlit-home`.
  - `t2-architect-shared-modules.yaml`: rows whose `used_by_units` includes `streamlit-home`, restricted by this unit's `shared_refs[].used_fields`.
  - `t2-architect-cross-unit-state.yaml`: flows touching the unit (currently none), plus the note on page-local state.
  - `t2-architect-migration-boundary.yaml`: rows in `must_rewrite`, `copy_as_is`, and `legacy_allowed_to_remain` that relate to this runtime.
- Before completion report: paths read, preserved behavior, unresolved/deferred contracts, import-boundary evidence and applicable contract/test/startup results. Do not claim current sources already expose REST or MCP behavior.

### Unit: `sample-library-seed`

- External trigger: `python -m sample_exam_builder`.
- Must read:
  - `units/sample-library-seed/behavior.yaml` — CLI effects, validation and SQLite writes.
  - `units/sample-library-seed/bindings.yaml` — package-module entrypoint.
  - `units/sample-library-seed/unit_decomposition.yaml` — advisory candidates only; `commit: false`.
- Relevant global rows:
  - `t2-architect-wire-contracts.yaml`: no row is assigned directly to the CLI; read the Groq-compatible generation contract because the seeder calls `ask_qwen`, not the Tutor, MyMemory or feed-import rows.
  - `t2-architect-shared-modules.yaml`: rows whose `used_by_units` includes `sample-library-seed`, restricted by its `shared_refs[].used_fields`.
  - `t2-architect-migration-boundary.yaml`: rows governing the seeder and its runtime dependencies.
- Before completion report: paths read, approved-library persistence behavior, unresolved/deferred work and isolated-database verification evidence.

## Global artifacts

- `t2-architect-unit-graph.yaml` — all current external triggers, source anchors, shared references and dependencies; use the current unit names `streamlit-home` and `sample-library-seed`.
- `t2-architect-migration-boundary.yaml` — user acceptance and runtime reachability; implementation scope is `must_rewrite`, not all source anchors.
- `t2-architect-wire-contracts.yaml` — current Groq, Tutor, MyMemory and RSS/Atom integration semantics; this repository has no pre-existing REST/MCP contracts.
- `t2-architect-shared-modules.yaml` — shared source used by both current units; filter by `used_by_units` and respect each `shared_refs.used_fields` allowlist.
- `t2-architect-cross-unit-state.yaml` — cross-unit findings; it intentionally has no rows because the current stateful UI is one page-level unit. Read its note for session state that must become explicit at the new transport boundary.
- `t2-architect-architecture.md` — current dependency graph, feature placement, coupling and migration risk evidence.
- `t2-architect-project-structure.md`, `t2-architect-tech-stack.md`, `t2-architect-data-model.md` — current package map, declared technology and SQLite schema/data behavior.
- `t2-architect.md` — task summary, upstream traceability and deliverable links.

## Unit: `streamlit-home`

- External trigger: Streamlit script `app.py`; one stateful page handles all current user-facing sections/actions.
- Must read:
  - `units/streamlit-home/behavior.yaml` — side effects, branches, error semantics and persistence boundary.
  - `units/streamlit-home/bindings.yaml` — Streamlit startup, fragment, session state and runtime configuration.
  - `units/streamlit-home/unit_decomposition.yaml` — advisory only; `commit: false`, not a target unit count decision.
- Relevant global rows: `wire_contracts.yaml` where `unit == streamlit-home`; shared modules where `used_by_units` includes this unit; state file note for the session-state lifecycle. No seam file was produced because no frozen legacy-side partial migration seam was declared or found.
- Before completion report: paths read, all preserved behavior items, any deferred contracts, and build/runtime/contract verification evidence. Do not claim endpoint or MCP behavior based on current sources.

## Unit: `sample-library-seed`

- External trigger: `python -m sample_exam_builder`.
- Must read:
  - `units/sample-library-seed/behavior.yaml` — CLI side effects, validation and SQLite writes.
  - `units/sample-library-seed/bindings.yaml` — package-module entrypoint.
  - `units/sample-library-seed/unit_decomposition.yaml` — advisory split candidates only (`commit: false`).
- Relevant global rows: `wire_contracts.yaml` has no row assigned directly to this CLI; read the Groq OpenAI-compatible generation row because the seeder calls `ask_qwen`, and do not treat Tutor, MyMemory or feed-import rows as CLI behavior. Read shared modules where `used_by_units` includes `sample-library-seed`; migration boundary rows for seeder/runtime files.
- Before completion report: paths read, persisted library semantics, unresolved/deferred work and isolated database/test evidence.

## Upstream Artifacts Consumed

- `.github/modernize/rearchitecture/clarification.md` — fixed stack and requirements.
- `.github/modernize/rearchitecture/artifacts/t1-teamlead.md` — constitution.
- `.github/modernize/rearchitecture/artifacts/t2.1-architect.md` — already-agreed HIGH-risk mitigations and acceptance evidence.
- `.github/modernize/rearchitecture/artifacts/t3-pm.md` — current behavior inventory used to scope source analysis.
- `.github/modernize/rearchitecture/artifacts/project-profile.yaml` — profile.

## Evidence Mapping

- `t2-architect-unit-graph.yaml#units` → unit navigation above.
- Global artifact row filters → specified per unit above.
- `units/*/behavior.yaml` → preservation and completion evidence requirement.
- `t2.1-architect.md#Mitigation decisions` → risk-control constraints referenced by the global and per-unit guides.
- `t3-pm.md#Feature Inventory` → source-unit behavior preservation scope.
