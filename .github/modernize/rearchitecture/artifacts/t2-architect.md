# t2 — Current Architecture Discovery

## Summary

The current application is a Python/Streamlit monolith, not a deployed web/API monorepo. `app.py` initializes SQLite and renders one stateful Streamlit page. UI functions directly call application services, AI functions, and (in places) SQLite-related code. Services call repositories and AI/provider code directly; repositories open SQLite connections directly. No FastAPI routes, MCP server, shared contracts package, DI/composition layer, or application ports exist yet.

The user-specified target therefore requires a vertical separation of UI, transports, application use cases, and infrastructure—not merely moving files. The critical migration issues are preserving Streamlit session state over HTTP, maintaining rights/consent and user-vs-library data rules, preserving existing database semantics without touching user data, and sharing application use cases across REST and MCP.

## Deliverables

- [architecture_index.md](./architecture_index.md) — per-unit implementation-guide navigation and artifact filters.
- [t2-architect-architecture.md](./t2-architect-architecture.md) — entrypoints, current layers/dependencies, risks, and target-boundary implications.
- [t2-architect-project-structure.md](./t2-architect-project-structure.md) — current package breakdown and measured file/LOC evidence.
- [t2-architect-tech-stack.md](./t2-architect-tech-stack.md) — existing runtime, dependencies, configuration and absent target frameworks.
- [t2-architect-data-model.md](./t2-architect-data-model.md) — SQLite tables, fields, relationships, and transaction observations.
- [t2-architect-unit-graph.yaml](./t2-architect-unit-graph.yaml) — current externally triggered units, signatures, dependencies and shared references.
- [t2-architect-migration-boundary.yaml](./t2-architect-migration-boundary.yaml) — runtime-reachable rewrite boundary; anchors are not themselves a task list.
- [t2-architect-wire-contracts.yaml](./t2-architect-wire-contracts.yaml) — current third-party and persistence-facing interfaces.
- [t2-architect-shared-modules.yaml](./t2-architect-shared-modules.yaml) — cross-unit shared-source inventory and supported public symbols.
- [t2-architect-cross-unit-state.yaml](./t2-architect-cross-unit-state.yaml) — explicit cross-unit state findings; Streamlit session state is currently intra-page.
- [units/streamlit-home/behavior.yaml](./units/streamlit-home/behavior.yaml), [bindings.yaml](./units/streamlit-home/bindings.yaml), [unit_decomposition.yaml](./units/streamlit-home/unit_decomposition.yaml) — current UI page contracts and non-committal split candidates.
- [units/sample-library-seed/behavior.yaml](./units/sample-library-seed/behavior.yaml), [bindings.yaml](./units/sample-library-seed/bindings.yaml), [unit_decomposition.yaml](./units/sample-library-seed/unit_decomposition.yaml) — current module CLI contracts.

## Findings for downstream design

- The only current application entrypoint is `app.py`; it calls `init_db()` and `views.home_page.render_home()`. The CLI `python -m sample_exam_builder` is a second entrypoint.
- Current user-facing behavior is a single Streamlit page with sidebar-selected Reading, Writing, Listening placeholder, and Speaking placeholder sections; exam, tutor, example-library and ingestion controls are nested on that page.
- `apps/web` must cease importing `services`, `ai`, `repositories`, `database`, and domain models. Those direct imports are present today in the Streamlit view.
- The target REST and MCP adapters need to call the same application use cases. No existing HTTP/MCP contract can be preserved; new versioned contracts must be specified during target design.
- `app.py` invokes `init_db()` on startup. That function creates/changes schema and commits. Do not start the current app or run tests against `data/yki.db`; use a temporary isolated database for downstream validation.
- This task is analysis-only. No application source, configuration, test, database, or user data was edited. No build/test/startup was run.
- `.github/modernize/rearchitecture/context.md` and `decisions.md` were absent; the board, clarification, constitution, profile, dependency artifacts and current source were used instead. The architect inbox contained prior routed notes; `architect/streamlit-stateful-cutover` was loaded and its session-state/isolated-database guidance was applied.

## Upstream Artifacts Consumed

- `.github/modernize/rearchitecture/clarification.md` — fixed target choices, safety boundaries, behavior-preservation baseline, and unresolved version/UI research limitations.
- `.github/modernize/rearchitecture/artifacts/t1-teamlead.md` — constitution invariants: thin transports over shared use cases, explicit module ownership, protected data/consent, and disabled identity/billing.
- `.github/modernize/rearchitecture/artifacts/t2.1-architect.md` — agreed mitigations and acceptance evidence for the seven HIGH migration risks.
- `.github/modernize/rearchitecture/artifacts/t3-pm.md` — current user-visible feature scope and behavior-preservation baseline.
- `.github/modernize/rearchitecture/artifacts/project-profile.yaml` — project sizing/stack summary and explicit dirty-worktree/data constraints.
- `.github/modernize/rearchitecture/board.md` — task request and migration scope.
- `README.md`, `requirements.txt`, and current application source — runtime, dependencies, entrypoints, and code relationships; `.env` and `data/yki.db` were not inspected.
- `.github/modernize/rearchitecture/learnings/architect/streamlit-stateful-cutover.md` — session-state and isolated-database migration guidance.

## Evidence Mapping

- `clarification.md#Backend` + `t1-teamlead.md#Architectural Invariants` → target boundaries and unresolved API/MCP design items in `t2-architect-architecture.md`.
- `t2.1-architect.md#Mitigation decisions` → accepted safeguards recorded as implementation controls in `t2-architect-architecture.md` and `architecture_index.md`.
- `t3-pm.md#Feature Inventory` → current capabilities whose source anchors and behavior contracts are recorded in the t2 artifacts.
- `t1-teamlead.md#IV Protect Existing Data, Consent, and Secrets` → data-safety and consent risks in `t2-architect-architecture.md` and `t2-architect-data-model.md`.
- `project-profile.yaml#project` → project-type/package-size evidence in `t2-architect-project-structure.md`.
- `requirements.txt` + `app.py` + imports in `views/`, `services/`, `repositories/`, and `ai/` → current stack and dependency graph in `t2-architect-tech-stack.md`, `t2-architect-unit-graph.yaml`, and `t2-architect-shared-modules.yaml`.
- `database/init_db.py` + repository connection/commit sites → schema and persistence contracts in `t2-architect-data-model.md` and `t2-architect-wire-contracts.yaml`.
