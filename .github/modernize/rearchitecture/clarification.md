---
schema: clarification/v1
generated_at: "2026-11-08T14:19:31Z"
scope:
  - frontend
  - backend
  - generic
clarity_score: 0.34
rounds: 1
gaps:
  - id: F1
    resolution: blocking
    note: "Streamlit is fixed, but no target version or version-retention policy was specified."
  - id: F2
    resolution: blocking
    note: "No component-library choice was supplied."
  - id: F3
    resolution: blocking
    note: "No screenshot, recording, or staging URL was supplied."
  - id: F4
    resolution: default
    default_used: "match existing pixel-by-pixel using extracted CSS custom properties"
  - id: F5
    resolution: default
    default_used: "WCAG 2.1 AA"
  - id: F6
    resolution: default
    default_used: "modern evergreen (Chrome, Firefox, Safari, Edge — latest 2 major versions)"
  - id: F7
    resolution: default
    default_used: "mobile-first using existing breakpoints detected from codebase"
  - id: F8
    resolution: default
    default_used: "preserve current locales; keep existing i18n library if present"
  - id: F9
    resolution: default
    default_used: "preserve existing pattern if identifiable; otherwise recommend minimal (component state + server-state library)"
  - id: F10
    resolution: default
    default_used: "use the de-facto router for the chosen target framework"
  - id: B1
    resolution: blocking
    note: "FastAPI is fixed, but no target version or version-retention policy was specified."
  - id: B2
    resolution: default
    default_used: "must preserve"
  - id: B3
    resolution: default
    default_used: "TBD / assess in research phase"
  - id: B5
    resolution: default
    default_used: "match current production baseline; no regression"
blocking_gaps:
  - id: F1
    note: "Target Streamlit version/version policy is unspecified."
  - id: F2
    note: "Target UI component approach/library is unspecified."
  - id: F3
    note: "No visual reference was supplied for the in-scope Streamlit UI."
  - id: B1
    note: "Target FastAPI version/version policy is unspecified."
---

# Scenario Clarification

## Frontend

- **Target framework**: Streamlit frontend, as specified. Exact version/version policy remains unresolved; select or retain a compatible version only after checking the project runtime/dependencies and official package metadata.
- **Component library**: Unspecified; no external or native component approach was selected.
- **Screenshots**: None supplied in the original request, latest message, or project profile.
- **Design system**: Match existing pixel-by-pixel using extracted CSS custom properties (default).
- **Accessibility**: WCAG 2.1 AA (default).
- **Browser targets**: Modern evergreen — Chrome, Firefox, Safari, and Edge, latest 2 major versions (default).
- **Responsive strategy**: Mobile-first using existing breakpoints detected from the codebase (default).
- **i18n locales**: Preserve current locales; keep existing i18n library if present (default).
- **State management**: Preserve existing pattern if identifiable; otherwise use a minimal approach (component state plus server-state library) (default).
- **Routing**: Use the de-facto routing approach for the chosen target framework (default).

## Backend

- **Target framework**: Separate FastAPI REST/BFF backend, as specified. Exact version/version policy remains unresolved; validate compatibility against the project runtime and official package metadata.
- **API contract preservation**: Must preserve (default); retain stable versioned REST/MCP contracts and existing observable behavior.
- **Data migration strategy**: TBD / assess in research phase (default). SQLite remains the stated persistence adapter; do not modify `data/yki.db` or other user data.
- **Auth framework**: Identity/authentication is an unimplemented, disabled extension point only; do not add functioning authentication.
- **SLA targets**: Match current production baseline; no regression (default). A baseline was not included in the supplied project facts.

## Generic

- **Success definition**: Migrate all existing functionality while preserving behavior, keeping the application runnable, and using shared application use cases behind the Streamlit, REST, and MCP adapters.
- **Out of scope**: Do not implement fake Listening/Speaking behavior; identity/authentication and billing remain disabled extension points, not functioning features. Preserve unrelated modules and pre-existing user changes.
- **Existing test posture**: The supplied baseline is 123 passing tests and two unrelated failures (`tests/test_article_ingestion.py::test_crawl_imports_eligible_full_text_and_skips_duplicate` and `tests/test_tutor.py::test_tutor_saves_lemma_and_inflection_from_grammar_answer`). Require the suite to pass except for those documented baseline failures; report all outcomes and risks.
- **Output location**: In-place in the current repository, using the requested `apps/`, `packages/`, `backend/`, and `infrastructure/` structure.
- **Additional constraints**: Do not inspect, copy, print, or edit `.env`; do not modify `data/yki.db` or other user data; preserve pre-existing uncommitted changes; do not commit or perform destructive Git operations. During this clarification task, do not modify source files. Verify exact package/API versions against official package metadata. Keep identity/authentication and billing as disabled extension points only.

## Clarification Evaluation

- **Frontend score**: 0.375 (required fields use the rubric's weights; missing required evidence scores zero; missing recommended fields score half; optional fields have no penalty).
- **Backend score**: 0.300.
- **Generic gate**: Pass — required success definition and in-place output location are specified.
- **Overall clarity score**: 0.3375, rounded to 0.34 (mean of the scored frontend and backend kits; the generic kit is a required-field pass/fail check).
- **Remaining blockers**: F1, F2, F3, and B1 are required fields without catalog defaults. They are recorded as blockers for downstream planning; no further question round is opened.

## Gaps & Defaults Applied

- F1 — blocking: exact Streamlit version/version policy not specified.
- F2 — blocking: target UI component approach/library not specified.
- F3 — blocking: no screenshots, recording, or staging URL supplied.
- F4–F10 — defaults applied as listed above.
- B1 — blocking: exact FastAPI version/version policy not specified.
- B2 — default: must preserve.
- B3 — default: defer data strategy to research.
- B5 — default: match current production baseline; no regression.

## Downstream Usage Notes

- Treat explicitly stated architecture, features, behavior, safety boundaries, and in-place location as resolved; do not ask another clarification round.
- Resolve the four blocking gaps through research/design decisions before they affect implementation. The user has instructed that no new clarification round is pending.
- Preserve the two documented baseline test failures as pre-existing only if verification confirms they remain unrelated.

## Upstream Artifacts Consumed

- `.github/modernize/rearchitecture/artifacts/project-profile.yaml` — project stack, target architecture/version verification note, and data-safety constraints.
- `.github/modernize/rearchitecture/clarification-questions.json` — read only its stored original `user_input` and question field list to recover the original request; no answer values were read.
- Original request recovered from that stored `user_input`, plus the latest user message — feature/behavior choices and explicit constraints.

## Evidence Mapping

- `project-profile.yaml#project` → project stack and data safety recorded in Backend and Additional Constraints.
- `project-profile.yaml#assessment.transformations` → Streamlit/FastAPI/MCP target architecture captured in Frontend and Backend.
- Original request (`clarification-questions.json#user_input`) → feature parity, module boundaries, shared use cases, enabled/disabled scope, test baseline, and in-place target reflected in Generic and Downstream Usage Notes.
- Latest user message → no new question round, in-place G4, and no source changes during this clarification task recorded in Generic.
