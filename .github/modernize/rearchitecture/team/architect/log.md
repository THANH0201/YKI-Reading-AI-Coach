## [t2] Current architecture discovery
- Codebase/domain discoveries: one stateful Streamlit page plus one sample-library CLI; views call services/AI directly, services call repositories/provider implementations, and SQLite initialization writes schema at startup.
- Important migration constraint: session-held article/exam/tutor state becomes an explicit HTTP contract; verification must use an isolated temporary database because app startup invokes `init_db()`.
- Wrong assumptions/corrections: there are no existing REST routes, MCP tools, or contract package to preserve; the app is not already split into frontend/backend deployments.
- Techniques/patterns worth reusing: use `app.py` and `python -m sample_exam_builder` as the current runtime roots; distinguish the active UI integration from unreferenced AI modules before cleanup.
- Learnings consumed: [teamlead/shared-use-cases-and-behavior-parity]

## [t2.1] Documenting mitigations for HIGH migration risks
- Codebase/domain discoveries: all seven HIGH findings in t2 have concrete architecture controls; the key new seam is an opaque API-owned transient exam session rather than trusting serialized Streamlit state or persisting learner text.
- Wrong assumptions and corrections: the target migration is not safe with only route-level validation; persistence eligibility and rights checks must live in shared application policy so REST and MCP cannot bypass them.
- Techniques/patterns worth reusing: require per-risk acceptance evidence and run contract, import-boundary, isolated-database, fake-provider, and cross-transport tests before declaring risk closure.
- Learnings consumed: [architect/streamlit-stateful-cutover]

## [t2] Revalidating current architecture and implementation navigation
- Codebase/domain discoveries: verified the two existing triggers (`app.py` Streamlit and `python -m sample_exam_builder` CLI), the direct UI → service/AI → repository/database coupling, Streamlit's hidden HTTP-session contract, and the absence of REST, MCP, and versioned contracts. `requirements.txt` pins Streamlit 1.66.1 but declares no FastAPI/MCP; active shell Python is 3.14.0.
- Wrong assumptions and corrections: an earlier summary said the architect inbox was empty and no learning existed; preflight found routed notes and `architect/streamlit-stateful-cutover`, and the summary now records them. The current task verified no source edit, ran no app/tests, and did not inspect `.env` or `data/yki.db`.
- Techniques/patterns worth reusing: keep the current unit graph distinct from t4's target module design; validate artifact completeness (unit count equals behavior/bindings/decomposition counts, candidate `commit: false`) and explicitly route each unit to its global artifact filters.
- Learnings consumed: [architect/streamlit-stateful-cutover]
