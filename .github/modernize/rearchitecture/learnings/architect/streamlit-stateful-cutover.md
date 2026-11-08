# Streamlit Stateful Cutover

The current Streamlit page's session state and startup schema initialization are latent contracts that must be made explicit when separating the UI from its backend.

## What Happened

For YKI Reading AI Coach task `t2`, source analysis found `app.py` initializes SQLite on application startup and `views/home_page.py` / `views/exam_page.py` keep article context, questions, answers, timer deadlines, and tutor/writing results in `st.session_state`. The current page also imports services and persistence-related functionality directly. The repository has no existing REST or MCP API to reuse.

## Takeaway

When moving a stateful Streamlit monolith behind HTTP, define the session/exam lifecycle and request/response contract before changing widgets; keep transient learner content transient. Inject/configure SQLite paths so startup and tests can use an isolated temporary DB; never launch the legacy entrypoint against user data during migration verification.

For this project, keep authoritative live-exam state behind an opaque API session handle in a bounded, transient store; do not trust a client round-trip of answers/deadlines or write personal exam data to SQLite. Use a single local API worker unless session storage is deliberately replaced, and fail clearly on restart/expiry. Put persistence eligibility and rights/consent gates in shared application use cases, with REST/MCP parity tests, so transport adapters cannot bypass them.

## History
- 2026-11-08 (YKI Reading AI Coach/t2): initial
- 2026-11-08 (YKI Reading AI Coach/t2.1): documented transient API-owned session and shared policy safeguards for REST/MCP.
