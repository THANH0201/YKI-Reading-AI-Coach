# Existing Technology Stack

## Runtime and dependencies

| Technology | Declared/current evidence |
|---|---|
| Language | Python; all application and test sources are Python. |
| Runtime in analysis shell | Python 3.14.0. |
| Supported Python range | Not declared in a root `pyproject.toml`, setup metadata, or requirements marker. The active runtime is evidence of this shell only, not a support guarantee. |
| UI/framework | `streamlit==1.66.1`. |
| LLM SDK | `openai==3.37.0`, used with `base_url=https://api.groq.com/openai/v1` and model `qwen/qwen3.8-27b`. |
| LLM/orchestration | `langchain>=1.0,<2`; `langchain-groq>=1.0,<2`; tutor additionally imports `groq` exceptions, `langgraph`, and Pydantic transitively. |
| Configuration | `python-dotenv==1.2.4`; current source calls `load_dotenv()` in model/tutor modules. This report does not inspect `.env`. |
| Persistence | Standard-library `sqlite3`; no external ORM is declared. |
| HTTP/feed | Standard-library `urllib`, `socket`, `ipaddress`, and XML/HTML parsers; Tutor also makes a MyMemory HTTP request. |
| Tests | `pytest>=8.3,<10`; `pytest-cov>=6,<8`. |

The requirements file does **not** declare FastAPI, an MCP SDK, JSON Schema/Pydantic contract package, or an HTTP client for the future Streamlit-to-API call. There is no current REST/MCP runtime. The exact transitive installed versions were not audited in this analysis.

## Provider bindings

- `ai/model.py` builds an `openai.OpenAI` client using the Groq-compatible base URL, `GROQ_API_KEY` from environment configuration, and `qwen/qwen3.8-27b`. It returns a dict containing `success` and `content` (plus an error on failure); callers perform task-specific parsing/validation.
- `services/tutor_service.py` separately creates `langchain_groq.ChatGroq` and uses LangChain agent tools and a maximum tool-call limit. It also calls MyMemory translation via `urllib`.
- This is two separate LLM call paths (general generation and tool-enabled tutor), not a unified provider abstraction.

## Framework bindings / compatibility facts

- Streamlit's page, widget, rerun and session-state APIs are used directly.
- A Streamlit `fragment` refreshes the exam timer each second.
- `python -m sample_exam_builder` is the package CLI entry.
- `requirements.txt` ranges do not pin LangChain/LangChain-Groq patch versions. No package lock or Python runtime declaration was found.
- No current package/API metadata establishes the compatibility of FastAPI/MCP with Python 3.14.0. Exact target versions and MCP Streamable HTTP library APIs remain for the design/implementation research gate; do not treat installed shell Python alone as proof of support.

## Upstream Artifacts Consumed

- `.github/modernize/rearchitecture/clarification.md` — fixed frameworks and unresolved exact target versions.
- `.github/modernize/rearchitecture/artifacts/t1-teamlead.md` — dependency workflow and target-stack constraints.
- `requirements.txt`, `ai/model.py`, `services/tutor_service.py`, `app.py` — current stack/binding evidence.

## Evidence Mapping

- `requirements.txt#all entries` → dependency table.
- `python --version` → current shell runtime evidence (not project support policy).
- `ai/model.py:1-68` → OpenAI SDK/Groq-compatible client and generation result behavior.
- `services/tutor_service.py:13-23, 781-806` → LangChain-Groq/Tutor integration.
- `clarification.md#Backend` + `t1-teamlead.md#Target Technology Stack` → absent target packages and version research limitation.
