# Current Architecture and Migration Risks

## Runtime shape

```text
Streamlit browser session
  -> app.py
     -> database.init_db.init_db() [first run in this Streamlit session]
     -> views.home_page.render_home()
          -> views.exam_page render functions
          -> services/* and ai/* directly
                -> repositories/* and SQLite directly
                -> Groq/OpenAI-compatible SDK, LangChain-Groq, MyMemory, RSS/Atom
```

`app.py` sets page configuration and shared CSS, then initializes the database once according to `_database_initialized` in `st.session_state`. There is no HTTP backend: no FastAPI app, route/router, REST contract, MCP server, or transport-neutral application boundary exists in the source tree. The second executable entrypoint is `sample_exam_builder/__main__.py`; `python -m sample_exam_builder` initializes the database and runs the library seeder.

## Existing layers and dependency direction

| Layer/package | Current responsibility | Observed coupling |
|---|---|---|
| `app.py`, `views/` | Streamlit composition and UI rendering; `home_page.py` owns section selection, article entry, exam-library controls, feed ingestion, writing, Listening/Speaking placeholders; `exam_page.py` owns exam/timer/result/tutor UI. | `home_page.py` imports business services, `ai.writing_analyzer`, model constants, `sqlite3`, and `exam_page.py`. `exam_page.py` imports scoring, timer, and tutor services. |
| `services/` | Reading orchestration, exam/library loading, scoring, feedback, timer, tutor, morphology, feed ingestion. | Services import AI functions, repositories, concrete SQLite errors, Groq/LangChain, and HTTP utilities directly. No ports/DI are present. |
| `ai/` | Level detection, classification, question generation, writing analysis and provider access. | `ask_qwen` creates an OpenAI SDK client pointed at Groq; separate tutor path constructs LangChain `ChatGroq`. `llm_router.py`, `prompts.py`, and `rag.py` are not imported by the active Python source found in this scan. |
| `repositories/`, `database/` | SQL statements and SQLite connection/schema creation. | Repositories call `database.db.get_connection()` directly. `database.db` opens the relative path `data/yki.db`; repositories independently open/commit/close connections. |
| `models/` | Dataclass records and exam-category rules. | Both services and repositories import these directly; they are not versioned transport schemas. |
| `sample_exam_builder/` | CLI-driven generation and saving of approved sample exams. | It shares question-generation, AI and persistence modules with the UI runtime. |

Dependency direction is not layered consistently: UI -> services/AI/models/SQLite; services -> AI/repositories/models/vendor clients; repositories -> database/models. `app.py` is both the UI launcher and database-startup composition root. There is no `backend/platform`, repository interface, application use-case package, transport composition root, or vendor-independent adapter. The root package names describe technology at a coarse level but do not yet match the requested module boundaries.

## Source-backed feature placement

- Reading analysis: `views/home_page.py` -> `services/article_service.py` -> `ai/level_detector.py`, `ai/subject_classifier.py`, `ai/question_generator.py` -> `ai/model.py`.
- Timed exam / scoring: `views/home_page.py` and `views/exam_page.py` retain active exam, deadline, article, questions, answers and results in Streamlit session state; `services/exam_timer_service.py` and `services/score_service.py` implement time and scoring; result/answer repositories persist eligible results.
- Example library: `ExamService.get_random_exam()` requests one approved article from each of four categories; `ArticleRepository` and `QuestionRepository` read them. `services/exam_service.py` also generates and saves approved articles.
- Feed ingestion and rights: `views/home_page.py` -> `ArticleIngestionService` -> feed-source repository, level/classification AI and `ExamService`; a feed must carry user-entered license/permission details and an explicit rights confirmation.
- Tutor: `views/exam_page.py` -> `TutorService`; LangChain agent/tools access vocabulary repository, morphology rules, Groq, and MyMemory. Article text is supplied as current-session context.
- Writing: `views/home_page.py` -> `ai.writing_analyzer.analyze_writing()` -> `ai.model.ask_qwen()`.
- Listening/Speaking: sidebar routes display explicit “not available yet” placeholders. There are no implementation functions to port.
- Sample-library CLI: `sample_exam_builder/__main__.py` -> `seeder.seed_sample_library()` -> AI/repositories and schema initialization.
- `ScoreService` constructs and returns `Feedback`, but the corresponding AI-feedback rendering in `views/exam_page.py` is commented out. Do not silently expose this as a new UI behavior during the move.

## Migration risks and mitigations

| Severity | Risk | Evidence and mitigation required |
|---|---|---|
| HIGH | Streamlit session state becomes a hidden API contract when the UI moves to HTTP. | Article content/ID, category, level, subject, questions, exam answers, deadline, auto-submit and tutor results are carried in `st.session_state`. Specify a versioned exam-session/request contract and explicit lifecycle; keep user-submitted text/results transient unless current behavior already persists approved-library exam results. |
| HIGH | Frontend can bypass the required backend boundary unless all direct imports are removed. | `views/home_page.py` imports services, AI, models and `sqlite3`; `views/exam_page.py` imports business services. Make `apps/web` depend only on an HTTP client and UI presentation models. |
| HIGH | Startup/testing may write user data. | `app.py` calls `init_db()`; it creates tables/indexes, applies additive `ALTER TABLE` statements and commits. Do not run current app/tests against `data/yki.db`; inject a temp DB through a connection/config seam and verify no user-data path is touched. |
| HIGH | Persistence semantics can drift while moving repositories. | Approved library articles alone are selectable; rights provenance is persisted; user-submitted reading text is session-only. Preserve `reuse_approved` filtering and the `exam_result_articles` link behavior. |
| HIGH | Rights and consent can be weakened when exposing new REST/MCP operations. | Feed import requires approval/rights fields plus checkbox confirmation, validates public feed URLs, avoids redirects, and applies size/entry/time limits. Keep these checks in shared use cases/policies, not just Streamlit form validation. |
| HIGH | REST/MCP may duplicate logic or diverge. | There are no existing API/MCP endpoints. Define application use cases once; transport handlers must adapt validated contracts and call the same use cases. Add cross-transport schema/error behavior tests. |
| HIGH | Two LLM integration paths have different semantics. | Reading/writing/seed use OpenAI SDK against Groq; Tutor uses `ChatGroq` with tools; translations use MyMemory. Keep all behind explicit infrastructure adapters and preserve structured JSON validation, tool limits, provider errors, and data-scope rules. |
| MEDIUM | Persistence operations do not share an evident unit-of-work boundary. | Article and questions are saved through separate commits; exam result and answers are also saved through separate repositories/commits. Preserve behavior initially and test failure/partial-write semantics before introducing transaction changes. |
| MEDIUM | A singular `article_id` coexists with multi-article exams. | `exam_results.article_id` points to one article while `exam_result_articles` records ordered multi-article association; session exams can have `article_id=None` and are not persisted. Preserve both cases. |
| MEDIUM | Runtime/version compatibility is unspecified for FastAPI/MCP. | Current Python executable is 3.14.0; no project Python floor/ceiling is declared. `requirements.txt` has no FastAPI or MCP dependency. Validate Python 3.14/package support and select MCP SDK/transport versions before implementation; do not infer availability from current environment alone. |
| MEDIUM | Partially present but unused AI modules can be mistaken for live behavior. | `ai/llm_router.py`, `ai/prompts.py`, `ai/rag.py` have no imports found in active Python files. Verify callers before moving or cleaning; do not silently revive them as new behavior. |
| MEDIUM | Pre-existing user changes must not be overwritten during migration. | The user and board explicitly require preserving the dirty worktree. Treat the checked-out contents as authoritative, preserve any unrelated changes, and avoid destructive Git operations or commits; this discovery task did not modify application source. |

## Architecture for the next design task

Use the user-fixed boundaries: Streamlit presentation + HTTP client in `apps/web`; REST/BFF and MCP Streamable HTTP as separate transport hosts; versioned contracts; module-owned application use cases for reading, writing, tutor and exam library; infrastructure adapters for SQLite and Groq; composition/policies/events in `backend/platform`. Identity and billing are disabled extension points only. This is target direction from the user/constitution, not an assertion that the current source already has these boundaries. The two current entrypoints and the stateful page are catalogued in `t2-architect-unit-graph.yaml`; split candidates remain advisory in the per-unit files.

## Upstream Artifacts Consumed

- `.github/modernize/rearchitecture/artifacts/t1-teamlead.md` — architecture invariants and required data/consent safeguards.
- `.github/modernize/rearchitecture/artifacts/t2.1-architect.md` — agreed mitigations and acceptance evidence for the seven HIGH risks; these remain implementation controls, not evidence of closure.
- `.github/modernize/rearchitecture/artifacts/t3-pm.md` — current user-visible feature scope and behavior-preservation baseline.
- `.github/modernize/rearchitecture/clarification.md` — fixed stack decisions and unresolved version choices.
- Current `app.py`, `views/`, `services/`, `ai/`, `repositories/`, `database/`, `models/`, and `sample_exam_builder/` — dependency and runtime evidence.

## Evidence Mapping

- `app.py:1-85`, `views/home_page.py:1-572`, `views/exam_page.py:1-377` → entrypoint/runtime flow and direct UI-to-business coupling.
- `services/` and `ai/` imports → layer dependency observations and vendor split.
- `t1-teamlead.md#II-III` → target adapter/module boundaries and shared use-case constraints.
- `t1-teamlead.md#IV` + `database/init_db.py:6-341` → user-data and schema-mutation risk.
- `t2.1-architect.md#Mitigation decisions` → already-agreed controls required to close the seven HIGH risks; this discovery does not claim their code-level acceptance evidence exists.
- `t3-pm.md#Feature Inventory` → feature areas that the source architecture must continue to support.
- `clarification.md#Backend` → unresolved exact FastAPI version and data migration strategy.
- `board.md#User Input` → preservation of pre-existing user work and no-commit/no-destructive-operation constraint.
