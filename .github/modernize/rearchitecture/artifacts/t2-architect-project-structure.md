# Existing Project Structure

## Classification

Current project type: **single Python application (Streamlit UI with local SQLite persistence and external LLM integrations)**. It is not currently a monorepo, separate frontend/backend deployment, REST API, MCP server, Python library, or standalone CLI product (although a sample-library seed CLI exists).

## Top-level package map

| Path | Current role | Evidence/count |
|---|---|---|
| `app.py` | Streamlit entrypoint, CSS/page configuration, per-session schema initialization, home renderer call. | 1 root Python file |
| `views/` | Streamlit UI: stateful home/navigation, reading and ingestion forms, writing, exam/timer/results and tutor rendering. | 2 Python files; 783 nonblank lines measured |
| `services/` | Application/business orchestration: article analysis, exam/library, timer, score, feedback, tutor, Finnish morphology, feed ingestion. | 8 files; 2,280 nonblank lines |
| `ai/` | AI prompts, provider access, classifiers/generators, writing analysis; three present modules had no active imports found. | 8 files; 453 nonblank lines |
| `repositories/` | SQLite query/persistence code for articles, questions, results, answers, vocabulary and ingestion feeds. | 6 files; 931 nonblank lines |
| `database/` | Relative SQLite connection and schema/index initialization/additive column upgrades. | 3 files; 270 nonblank lines |
| `models/` | Python dataclasses and exam-category/word-count/question-distribution rules. | 6 files; 91 nonblank lines |
| `sample_exam_builder/` | `python -m` entrypoint and generated approved sample-exam seeder; includes its own test file. | 4 Python files; 649 nonblank lines |
| `tests/` | Unit/service/repository/Streamlit and AI behavior tests. | 15 files; 2,606 nonblank lines |
| `data/` | User/library database and other runtime data. | Excluded from inspection; do not edit. |
| `docs/`, `prompts/` | Documentation and prompt/data support; not independent runtime applications. | No `.py` files in measured scan |

`project-profile.yaml` records 8,131 nonblank Python lines. The direct folder counts above were collected from the working tree; line totals are folder-specific and include tests where noted. Existing dirty/untracked changes mean these values describe this checkout, not a pristine release.

## Layers (as implemented, not as intended)

1. **UI/host** — `app.py`, `views/home_page.py`, `views/exam_page.py`.
2. **Service orchestration/business rules** — `services/*.py`.
3. **AI/vendor calls** — `ai/*.py`, plus direct Groq/LangChain/MyMemory use in tutor service.
4. **Persistence** — `repositories/*.py` and `database/*.py`.
5. **Models** — `models/*.py`.

These are package groupings, not enforced dependency boundaries. The UI imports business logic directly; service functions/classes import repositories and AI implementations; repositories import the concrete connection function.

## Entrypoints and configuration

- `streamlit run app.py` (or equivalent): page config/style, session-guarded `init_db()`, then `render_home()`.
- `python -m sample_exam_builder`: calls `init_db()` and runs `seed_sample_library()`.
- `requirements.txt`: only Python package manifest; no `pyproject.toml`, `setup.cfg`, or `pytest.ini` was found at repository root.
- `database/db.py`: SQLite `connect("data/yki.db")`, with foreign keys enabled.
- `.gitignore`: present; not a runtime configuration boundary.
- `views/exam_page.py`: `@st.fragment(run_every="1s")` timer callback.
- No FastAPI, MCP, REST router, transport contract schema, API host, composition root, or runtime dependency-injection module exists.

## Functionality surfaced from the page

Reading analysis and timed exams, approved example exams/library, licensed RSS/Atom import, AI Tutor, writing practice, and explicit unavailable Listening/Speaking placeholders all route through the single stateful home page. The current structure does not provide one deployable/package boundary per business capability.

## Upstream Artifacts Consumed

- `.github/modernize/rearchitecture/artifacts/project-profile.yaml` — sizing and package summary.
- Current repository path inventory and package line-count command — folder evidence.
- Current `app.py`, `views/`, `sample_exam_builder/`, and `requirements.txt` — entrypoints and configuration.

## Evidence Mapping

- `project-profile.yaml#project` → recorded project type/sizing.
- `app.py:1-85`, `sample_exam_builder/__main__.py:1-25` → entrypoints.
- Package file inventory and nonblank line counts → package table.
- Source imports in views/services/repositories → actual layer relationships.
