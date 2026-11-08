ự viết bộ phân tích và sinh dạng từ bằng code của project, không dùng Omorfi hay gọi AI để sinh paradigm. 
Tôi đề xuất cấu trúc như sau:

Bảng	Dữ liệu
vocabulary_words	Lemma, nghĩa, từ loại, thông tin chung
noun_forms	Cách, số ít/số nhiều, dạng từ
verb_forms	Loại động từ, thân từ và dạng chia theo ngôi, thì, thức, chủ động/bị động, khẳng định/phủ định
adjective_forms	Dạng cách/số, so sánh hơn và so sánh nhất
other_word_forms	Biến thể phù hợp cho đại từ, trạng từ và các từ loại khác
# YKI Reading AI Coach

## Run the app

Install the project dependencies and start Streamlit from the repository root:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\streamlit.exe run app.py
```

Set `GROQ_API_KEY` in the local environment (or `.env`) for AI level detection,
subject classification, question generation, and tutor answers. The SQLite
schema is initialized automatically when a Streamlit session starts.

Article text entered by a learner is sent to the configured AI provider for
analysis but is not written to SQLite or added to the sample-exam library.
The generated practice exam and score remain in the active Streamlit session.
Sample exams come only from the separate curated library; adding an article
requires a recorded rights basis, permission reference, and reviewer. The app
does not ship with licensed Yle article content.

The home page includes an opt-in RSS/Atom ingestion workflow for sources
whose license or written permission explicitly allows full-text storage,
question adaptation, AI-provider processing, and learner display. Registering
a source records the rights evidence and reviewer, then imports eligible
items from the feed's own full-text content. It does not crawl linked article
pages. The four capped pools each allow 10 approved texts (40 total): notices,
advertisements, and messages (20-100 words, four multiple-choice questions);
emails, letters, and instructions (100-250 words, four true/false questions);
Utiset (300-600 words, B2, five open questions); and Selkouutiset
(300-600 words, B1, five open questions). Open questions must have a stored
model answer and scoring keywords. Re-running a registered feed skips article
URLs already imported. Users can run one registered feed or all registered
feeds from the UI; ingestion is started on demand rather than scheduled in
the background. A random sample exam combines one article from each pool,
with 18 questions total, and links the saved result to all four source
articles. Generated answer keys are references and should be reviewed before
formal assessment. The app records but does not independently verify
licensing claims; reference sites are not treated as licensed article
sources.

An optional sample-exam builder is isolated in `sample_exam_builder/`; the
Streamlit application does not import it. From the project root, run
`python -m sample_exam_builder` to create original synthetic Finnish practice
materials through the configured Groq API and store them in the four pools.
A complete empty-library seed creates 40 texts and 180 questions
(10 per pool); prompts instruct the model not to copy or adapt publisher
articles, and the seeder validates lengths, question types, and answer keys.
This API operation can incur charges. The texts are synthetic exercises, not
authentic published news. Removing `sample_exam_builder/` disables only this
optional generator and its focused tests; existing database content and app
features remain available. Shared application models, repositories, and AI
client modules intentionally stay outside the optional folder.

The Tutor can answer Finnish vocabulary questions even when no article is
loaded. When an article is active, it can search the current article locally
and explain a word using a matching sentence; without one, it gives a general
vocabulary explanation. It can translate Finnish words or short phrases
through the MyMemory Finnish-English API. Translation requests
send only the requested word or phrase to MyMemory; an internet connection is
required, but no separate API key is needed. For vocabulary questions, the
Tutor also explains the word's lemma, part of speech, relevant inflection and
why that form appears in context. For verbs it explains the verb type (1-6)
and stem/form change when it can identify them reliably; ambiguous forms are
flagged rather than presented as certain.
Successful Finnish-English translations are cached in the local SQLite
`vocabulary_translations` table. The Tutor checks this cache first and calls
MyMemory only when the normalized phrase has no saved translation.
When the learner asks about one Finnish word, the Tutor saves the entry under
its dictionary lemma (for example, `kotona` is keyed by `koti`) and records
the queried form, a concise meaning, part of speech, noun countability or
Finnish verb type, suffixes, grammatical features, stem changes, and current
article/topic context in `vocabulary_words`. Before invoking the Groq agent,
the Tutor checks the lemma and known inflected forms in this cache. A hit with
a saved meaning is answered from SQLite without a Groq call; a cache miss is
analyzed by the AI and saved. The queried form is included in the saved noun
paradigm when its case and number are known. Noun forms are stored in
`vocabulary_word_forms` by grammatical case, number, and actual form (for
example, `koti` has `partitive/singular = kotia` and `partitive/plural =
kotoja`). Suffixes and feature sets use JSON to accommodate analyses that
vary by word.

The Tutor uses a LangChain agent to orchestrate the Groq chat model and its
allowlisted tools, with a per-run tool-call limit. Other AI features in the app
still call the OpenAI-compatible Groq SDK directly.

## Test

Run the full test suite and statement coverage report:

```powershell
.\venv\Scripts\python.exe -m pytest -q --cov=ai --cov=services --cov=repositories --cov=models --cov=database --cov=views --cov=app --cov-report=term-missing
```

Tests use mocked AI responses and temporary SQLite databases; they do not
require the external AI service or modify the application's database.