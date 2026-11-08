## [clarifying-scenarios-resume] Completed scenario clarification
- Codebase/domain discoveries: Project-profile records a Python/Streamlit YKI Reading AI Coach, 8,131 LOC, with the target modular FastAPI + MCP Streamable HTTP architecture; source tree, user data, and `.env` were not inspected.
- Wrong assumptions and corrections: The clarification question file held the original request in `user_input`; its answer fields were not used. No submitted answers markdown existed, so the latest user message was applied as the answer supplement without opening another question round.
- Debugging dead-ends and what actually worked: `context.md`, `board.md`, `decisions.md`, and teamlead inbox/history were absent. The project profile and stored original request were sufficient to produce the canonical artifact.
- Techniques/patterns worth reusing: Record absent required fields with no catalog default as blocking gaps and follow the clarification skill's Step 5/6 path to produce READY without re-asking.
- Learnings consumed: [(none)]

## [t1] Defined behavior-preserving rearchitecture guardrails
- Codebase/domain discoveries: The requested target is a Python/Streamlit application with a pinned Streamlit dependency; the clarification and board specify FastAPI, MCP Streamable HTTP, shared feature parity, data protection, and disabled identity/billing.
- Wrong assumptions and corrections: `context.md`, `decisions.md`, and teamlead inbox were absent; clarification and the board were the authoritative task inputs. No source code, `.env`, or database file was inspected.
- Debugging dead-ends and what actually worked: `Get-Date -AsUTC` is unavailable in this PowerShell version; `[DateTime]::UtcNow` provided the required UTC timestamp.
- Techniques/patterns worth reusing: Keep web/API/MCP as adapters over module-owned application use cases; specify protected data and transport parity as testable invariants.
- Learnings consumed: [(none)]
