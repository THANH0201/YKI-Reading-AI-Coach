## 2026-11-08T14:25:04Z — teamlead (t1)
Constitution v1.0.0 is ready at `.github/modernize/rearchitecture/artifacts/t1-teamlead.md`. It requires behavior parity, client-only Streamlit, shared use cases behind REST and MCP adapters, protected data and consent, disabled identity/billing, and tests at the contract and feature boundaries.

## 2026-11-08T14:35:40Z — architect (t2)
HIGH: Current Streamlit views call services, AI and persistence code directly; the target requires an HTTP-only frontend and shared application use cases behind REST and MCP.

## 2026-11-08T14:35:40Z — architect (t2)
HIGH: `app.py` runs schema initialization at startup. Use an isolated temporary database for verification; this task did not start the app or access `data/yki.db`.

## 2026-11-08T14:35:40Z — architect (t2)
INFO: The current app has no REST routes, MCP tools or versioned API contracts. Exact target framework/SDK versions and Python support still need verification.

## 2026-11-08T14:35:40Z — pm (t3)
Feature inventory and acceptance scenarios REQ-001–REQ-017 are ready at `.github/modernize/rearchitecture/artifacts/t3-pm.md`; these define the behavior-parity checklist and persistence boundaries.

## 2026-11-08T14:44:20Z — architect (t2.1)
Downstream design guardrails: preserve opaque transient exam state, keep Streamlit HTTP-only, use isolated SQLite test databases, enforce rights and persistence in shared use cases, and call the same use cases from REST/MCP. Keep Groq, Tutor, and MyMemory adapter behaviors distinct. In-memory sessions require one API worker and expire on restart.
