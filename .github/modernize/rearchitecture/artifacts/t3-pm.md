# t3 — Existing User-Facing Feature and Behavior Inventory

**Role:** PM  
**Phase:** Discovery  
**Status:** Ready for design and parity planning  
**Inventory basis:** Current Streamlit screens, their backing user journeys, and existing tests.

## Scope Baseline

- **Discovery method:** Read the current Streamlit entry point and screen renderers; traced the corresponding service behavior and examined UI, service, and repository tests. No `.env` or user database contents were accessed.
- **Total user-facing feature areas discovered:** 7.
- **Items in scope:** 7 — Reading practice, sample exams, timed exam/scoring, AI Tutor, Writing practice, licensed-feed library management, and Listening/Speaking placeholders.
- **Out of scope as current functionality:** Functional identity/authentication and billing; these are disabled extension points, not user-visible capabilities. Do not invent Listening or Speaking exercises.

## Upstream Artifacts Consumed

- `.github/modernize/rearchitecture/artifacts/t1-teamlead.md` — behavior-preservation guardrails, privacy/rights constraints, and parity acceptance baseline.
- `.github/modernize/rearchitecture/clarification.md` — confirmed target behaviors and non-functional constraints; explicit user choices are treated as resolved.

## Evidence Mapping

- `t1-teamlead.md#Core Principles I, IV` → parity, consent/rights, privacy, and protected-data requirements in REQ-001–REQ-006 and REQ-014–REQ-017.
- `t1-teamlead.md#Architectural Invariants` → inventory boundary: observable behavior is specified here; target implementation details remain for the architecture artifact.
- `clarification.md#Backend` and `clarification.md#Generic` → FastAPI/MCP migration must retain these capabilities; disabled identity/billing and no fake Listening/Speaking are recorded as out of scope.
- Current `views/home_page.py`, `views/exam_page.py`, service/AI modules, README, and existing tests → feature scenarios and observable behavior below.

## Feature Inventory

| ID | User-facing area | Current observable behavior | Priority |
|---|---|---|---|
| F-01 | Reading practice | Learner submits Finnish text; receives supported-level/subject feedback and generated reading questions; text is disclosed as sent to the configured AI provider and not saved to the sample library. | P1 |
| F-02 | Example Reading Exam | Learner can load a randomly assembled approved sample exam, see its reading materials/questions, and begin the timed exam immediately. | P1 |
| F-03 | Timed exam and scoring | Learner answers multiple-choice, true/false, and open questions, submits or is auto-submitted at 30 minutes, and sees score and per-question correctness. | P1 |
| F-04 | AI Tutor | Learner asks vocabulary, grammar, or article-context questions; sees an answer or a clear failure message. Vocabulary support can work without a loaded article. | P1 |
| F-05 | Writing practice | Learner submits Finnish writing and receives a non-official B1/B2 estimate, feedback, corrections, suggestions, and a suggested revision. | P2 |
| F-06 | Licensed-feed sample library | A library maintainer enters source/license/approval details and confirms reuse rights; the app imports eligible feed content, reports outcomes, and shows category capacity. | P2 |
| F-07 | Listening and Speaking | Navigation entries lead to explicit “not available yet” placeholders. There is no Listening or Speaking exercise behavior. | P3 (preserve placeholder) |

### User Story 1 — Practice reading with personal text (P1)

As a learner, I want to paste a Finnish article and receive a level estimate, topic, and practice questions so that I can practice reading comprehension.

**Why this priority:** This is the core practice journey.

**Independent test:** Enter supported Finnish text, analyze it, and verify feedback and a complete five-question practice exam without relying on the sample library.

**Acceptance scenarios:**

1. **Given** an empty or whitespace-only article, **when** the learner selects **Analyze Reading**, **then** the app asks for article content and does not proceed with analysis.
2. **Given** a text whose level cannot be determined, subject cannot be classified, or valid questions cannot be generated, **when** analysis runs, **then** the app displays a failure message and clears stale prior exam/question state.
3. **Given** a detected level of A2, **when** analysis runs, **then** the learner is told the text is unsuitable for YKI practice and is asked to choose a longer, more challenging article.
4. **Given** a supported level B1, B2, or C1 and successful topic/question generation, **when** analysis completes, **then** the app shows the level and subject and makes **Start Exam** available.
5. **Given** a successful analysis, **when** the learner starts the exam, **then** the app presents the generated questions, the reading text, an active 30-minute timer, and the Tutor.
6. **Given** a personal article or its exam result, **when** analysis and scoring complete, **then** neither the article nor its exam result is added to the sample-library or saved exam-result records.

### User Story 2 — Take an example reading exam (P1)

As a learner, I want a ready-made exam drawn from approved materials so that I can practice without preparing my own article.

**Why this priority:** The sample exam offers a complete, repeatable practice path.

**Independent test:** Load an exam from a library containing eligible content in all four categories and complete it through its result screen.

**Acceptance scenarios:**

1. **Given** approved eligible articles exist in all four categories, **when** the learner selects **Example Reading Exam**, **then** the app loads one article per category and starts a 30-minute exam.
2. **Given** a sample exam is loaded, **when** it is displayed, **then** the learner can read each article and answer its associated questions; original synthetic practice material, when present, is identified as synthetic rather than publisher news.
3. **Given** no complete example exam is available, **when** the learner selects the button, **then** the app reports that no example exam is available and does not present an incomplete exam.
4. **Given** an active or completed example exam, **when** the learner selects **Home**, **then** exam state, answers, and displayed exam materials are cleared and the Reading screen returns.

### User Story 3 — Complete and review a timed exam (P1)

As a learner, I want to answer questions under a fixed time limit and review my score so that I can assess my practice.

**Why this priority:** Timing, scoring, and question review complete the exam experience.

**Independent test:** Answer representative question types, submit, and verify score, correct-answer count, and question review; separately exercise timer expiry.

**Acceptance scenarios:**

1. **Given** an exam starts, **when** the learner views the timer, **then** it begins at 30:00 and counts down to zero.
2. **Given** an unanswered exam, **when** the learner submits it, **then** unanswered responses are included and the result shows percentage score, correct/total count, and question-level correctness.
3. **Given** a choice answer differing only in case or surrounding whitespace from its answer key, **when** it is graded, **then** it is treated as correct.
4. **Given** an open response, **when** it contains the required portion of the question’s keywords (at least 60%, rounded to an integer and at least one), **then** it is marked correct; malformed/missing keyword data does not mark it correct.
5. **Given** the timer reaches zero, **when** the exam has not already been submitted, **then** the app submits the answers once, disables further answering, and states that submission was automatic.
6. **Given** a saved approved sample exam, **when** it is graded, **then** the result and answers are retained; **given** a personal-text exam, **then** its result remains session-only.
7. **Given** an exam has no questions or a question type is unsupported, **when** scoring/rendering occurs, **then** the app does not score an empty exam and communicates that the question is unsupported rather than treating it as correct.

### User Story 4 — Ask the AI Tutor (P1)

As a learner, I want to ask a question about Finnish vocabulary, grammar, or the current article and receive an answer, so that I can understand what I read.

**Why this priority:** Contextual explanations are a core support capability alongside practice.

**Independent test:** Ask a vocabulary question without an article and an article-context question with an article, then verify answer/failure display.

**Acceptance scenarios:**

1. **Given** the Reading screen is open, **when** the learner submits a non-empty question, **then** the question is cleared from the input while the Tutor prepares and displays the answer.
2. **Given** an article is loaded, **when** the learner asks about its content or a word in it, **then** the Tutor can use that article context.
3. **Given** no article is loaded, **when** the learner asks a Finnish vocabulary or grammar question, **then** the Tutor can still respond.
4. **Given** the Tutor or a supporting translation service fails, **when** the request completes, **then** the app shows a warning/failure message instead of presenting the failure as a successful answer.
5. **Given** vocabulary analysis or translation has been successfully produced, **when** it is looked up again, **then** existing vocabulary/translation knowledge may be reused; article text itself remains governed by the session-only personal-text behavior.

### User Story 5 — Practice Finnish writing (P2)

As a learner, I want feedback on Finnish writing so that I can understand strengths and improve grammar, vocabulary, and sentence structure.

**Why this priority:** Writing practice is a separately available skill, but Reading remains the primary product journey.

**Independent test:** Open **Writing**, submit Finnish text, and verify feedback sections; verify blank and invalid/provider responses.

**Acceptance scenarios:**

1. **Given** the learner enters Finnish text and selects **Analyze Writing**, **when** analysis succeeds, **then** the app shows a B1 or B2 estimate, Vietnamese-language assessment/feedback, available strengths, corrections, sentence suggestions, and a complete suggested Finnish revision.
2. **Given** the returned analysis identifies no corrections, **when** the result is displayed, **then** the app says no clear spelling or grammar errors were identified.
3. **Given** the text is blank, the service is unavailable, or the model returns invalid/incomplete data, **when** the learner analyzes it, **then** the app requests text or shows a readable warning and does not show stale results for different text.
4. **Given** any writing result is displayed, **then** it is identified as practice feedback, not an official YKI score.

### User Story 6 — Maintain the licensed sample library (P2)

As a library maintainer, I want to register a licensed RSS/Atom feed and review import outcomes so that only eligible, approved content becomes an example exam.

**Why this priority:** The sample-exam journey depends on properly approved, valid library content.

**Independent test:** Register a feed with all required rights details and explicit confirmation; verify eligible items import and duplicate/ineligible items are reported as skipped or failed.

**Acceptance scenarios:**

1. **Given** the feed form is displayed, **when** the maintainer registers a source, **then** Publisher, YKI article type, feed URL, rights basis, evidence reference, approver, and explicit rights confirmation are required.
2. **Given** rights are not confirmed or required source details are missing, **when** registration is submitted, **then** import is refused with an actionable message.
3. **Given** the source is accepted, **when** its RSS/Atom feed is processed, **then** only full text present in the feed is considered; the app does not fetch separate article pages.
4. **Given** an entry is already imported, too short/long, at the wrong required level, unable to classify, or unable to produce the category question format, **when** a feed is processed, **then** it is skipped or reported failed and is not added as an eligible exam.
5. **Given** a valid new entry, **when** it passes reuse approval, content/category/level rules, and question validation, **then** it is imported and reported with its title and relevant metadata.
6. **Given** registered sources exist, **when** the maintainer chooses an individual source or **Fetch all registered feeds**, **then** the selected sources are processed on demand and per-source/item outcomes are displayed.
7. **Given** the library page is shown, **when** capacity is available, **then** category pool counts are visible; each category has a maximum of 10 articles.
8. **Given** a source feed URL is submitted, **when** it is invalid, does not resolve only to public IP addresses, or redirects, **then** it is rejected rather than fetched.
9. **Given** any license details or checkbox confirmation, **then** the app records the maintainer’s assertion but does not claim to verify the license independently.

### User Story 7 — See unsupported skill status (P3)

As a learner, I want to know whether Listening and Speaking practice is available so that I am not misled into expecting exercises that do not exist.

**Independent test:** Select each sidebar entry and verify an explicit unavailable message without exercise controls or fabricated results.

**Acceptance scenarios:**

1. **Given** the learner selects **Listening**, **when** the section opens, **then** it identifies Listening Practice as not available yet and describes it as a future-audio placeholder.
2. **Given** the learner selects **Speaking**, **when** the section opens, **then** it identifies Speaking Practice as not available yet and describes it as a future-speaking placeholder.

## Functional Requirements

- **REQ-001:** The application MUST provide the current Reading, Example Reading Exam, Writing, Listening, and Speaking navigation entries, default to Reading, and retain each entry’s current available/placeholder behavior.
- **REQ-002:** The Reading journey MUST reject empty content; estimate a level and classify a subject; accept B1, B2, and C1; reject A2 as unsuitable; and present a readable failure when level, classification, or question generation cannot complete.
- **REQ-003:** A successful personal-article analysis MUST produce exactly five questions in the current distribution: two multiple-choice, two true/false, and one open question. Multiple-choice questions have four options and a matching answer; true/false uses True or False; open questions use keyword-based grading.
- **REQ-004:** Personal article text MUST be disclosed to the learner as being sent to the configured AI provider, MUST NOT be saved to the example library, and MUST remain session-only. The existing screen presents a disclosure, not a separate user opt-in checkbox; migration MUST NOT silently change that fact or claim a consent step that does not exist.
- **REQ-005:** Starting a personal exam MUST start a 30-minute timer and expose its generated questions, reading material, Tutor, and submit action.
- **REQ-006:** The Example Reading Exam MUST select only approved/eligible material and require a complete exam with one article from each current category: notice, email, Utiset, and Selkouutiset. The current category formats are respectively four multiple-choice, four true/false, five open B2, and five open B1 questions (18 total); a missing complete sample MUST produce the current unavailable warning.
- **REQ-007:** A loaded example exam MUST display its reading materials with category, title, level, subject, and word count; identify synthetic original text when applicable; and start its timer automatically.
- **REQ-008:** Exam scoring MUST compare choice answers case-insensitively after trimming whitespace; grade open answers against at least 60% of valid keywords, rounded with a minimum of one; and mark unsupported question types incorrect.
- **REQ-009:** Exam results MUST display score percentage, correct/total count, correct/incorrect question review, and an automatic-submission notice where time expired. After submission, answer controls MUST be disabled and repeated timer callbacks MUST NOT submit twice.
- **REQ-010:** Only approved library-exam results and associated submitted answers MUST be persisted. Personal-text exam questions/results MUST remain session-only. Successful Tutor vocabulary/translation analysis may be stored in vocabulary records/cache as in the current behavior.
- **REQ-011:** The Tutor MUST accept vocabulary, grammar, and article-content questions; operate without an article for general vocabulary help; use available article context when present; and display either a successful response or a warning for failures.
- **REQ-012:** Writing analysis MUST provide a B1/B2 estimate, an explicitly non-official assessment, strengths, actual spelling/grammar corrections, optional sentence/vocabulary suggestions, and a meaning-preserving Finnish revision; empty or invalid/unavailable responses MUST be handled without stale analysis.
- **REQ-013:** Licensed-feed intake MUST retain its explicit rights confirmation and required metadata, on-demand crawl controls, per-item imported/skipped/failed outcomes, and pool counts; it MUST not claim that license evidence was independently verified.
- **REQ-014:** Feed ingestion MUST accept only valid public HTTP(S) feed URLs without redirects, use RSS/Atom content without fetching linked article pages, require full text and category word-count/level/question rules, skip duplicates, and cap each category at 10 articles.
- **REQ-015:** Listening and Speaking MUST remain clearly labeled unavailable placeholders; no fake exercise or result behavior may be introduced.
- **REQ-016:** Functional identity/authentication and billing MUST NOT be represented as existing user features or be enabled as part of feature parity.
- **REQ-017:** Legal/rights disclosures MUST remain visible at the same decision points: personal-text processing disclosure, licensed-feed warning, and affirmative feed-reuse confirmation. The warning MUST continue to state that the app does not verify rights or automatically crawl reference sites.

## Key Entities (user-observable)

- **Practice article:** learner-provided, session-only article text with detected level, subject, and generated questions; distinct from approved library material.
- **Approved sample article:** reusable article with category, content, source, level, subject, and approval/license evidence.
- **Exam question and answer:** question kind, prompt, answer options where applicable, answer key, open-answer keywords, and learner response.
- **Exam result:** score, correct/total counts, per-question review, and—for saved sample exams—associated answers and article set.
- **Tutor vocabulary record:** Finnish word form and lemma, meaning, grammatical information, and generated forms; translations may be cached for reuse.
- **Feed source:** publisher, feed URL, exam category, rights basis/evidence, approver, confirmation, and last-check status.
- **Writing analysis:** estimated level, assessment, strengths, corrections, suggestions, and revised text.

## Edge Cases to Preserve

- The learner may switch between Reading and other skills; Listening/Speaking must not imply real functionality.
- Failed reading analysis must clear the old exam and answers so stale questions are not shown as the new result.
- A sample exam is unavailable when any required category lacks eligible material; do not silently return a partial exam.
- Empty exams cannot be graded. Unsupported question kinds are warned about and do not receive credit.
- Timer expiry races with a manual submit must still produce only one result.
- Feed registration can fail for missing rights evidence, a false confirmation, invalid category/URL, unavailable database/network, invalid feed content, or ineligible entries. Report actionable failures without importing rejected content.
- A registered feed may have no new eligible entries because all entries are duplicates, out of range, or the category quota is full; show skips rather than implying import success.
- Tutor may fail due to provider, tool, or translation service errors; never render an error as a successful explanation.
- Writing model output may be malformed, incomplete, or refer to text different from the current input; do not display invalid or stale output.
- An approval record is a maintainer assertion, not proof of legal rights; the UI warning and confirmation remain necessary.

## Success Criteria

- **SC-001:** All seven discovered feature areas are explicitly accounted for in the migrated product; zero current features are silently omitted.
- **SC-002:** A learner can complete both a personal-text reading session and an approved sample exam, including submission and result review, with the recorded behavior above.
- **SC-003:** Personal article text and its practice result do not appear in the sample library or saved sample-result history; approved sample exam results remain reviewable through their existing persistence behavior.
- **SC-004:** The two currently supported skill placeholders remain visibly unavailable, and the migrated app presents no fake Listening/Speaking exercise.
- **SC-005:** The feed workflow preserves rights disclosures/confirmation and rejects ineligible, duplicate, or unapproved materials from the sample exam pool.
- **SC-006:** Tutor and Writing success and failure states remain distinguishable and do not display stale or fabricated success results.

## Assumptions and Inventory Limitations

- This artifact records the existing product behavior, not a design for new behavior. If implementation evidence conflicts with this inventory, preserve source-backed behavior and notify the coordinator with the exact discrepancy.
- The current application exposes feed-library controls in the Streamlit interface; no role-based/admin authentication flow was evidenced. This inventory does not imply that feed controls are protected by an account system.
- The personal reading form explicitly discloses AI-provider processing and session-only storage. No separate consent checkbox is present for personal reading. Feed ingestion does have a separate affirmative rights checkbox.
- The result page currently displays score and question review; the service's generated AI-feedback object is not rendered as part of the current UI.
- Functional identity and billing are not current capabilities; they are excluded from parity.
- This was a discovery task. Existing tests were inspected as evidence, but no test suite was executed.

## Evidence Sources

- `app.py` — current application title, page setup, and initialization entry.
- `views/home_page.py` — navigation, reading form/disclosure, writing, feed library controls, and skill placeholders.
- `views/exam_page.py` — question types, timer, exam results, and Tutor interactions.
- `services/article_service.py`, `services/exam_service.py`, `services/score_service.py`, `services/article_ingestion_service.py` — observable validation, selection, scoring, persistence eligibility, and ingestion outcomes.
- `ai/question_generator.py`, `ai/level_detector.py`, `ai/subject_classifier.py`, `ai/writing_analyzer.py` — current content validation and analysis constraints.
- `models/exam_category.py` — category word-count/level/question-distribution rules and capacity.
- `services/tutor_service.py` and `repositories/vocabulary_repository.py` — Tutor capabilities and retained vocabulary behavior.
- `tests/test_app.py`, `tests/test_services.py`, `tests/test_article_ingestion.py`, `tests/test_exam_generation.py`, `tests/test_tutor.py`, and `tests/test_writing_analyzer.py` — existing UI/service behavior evidence.
- `README.md` — documented learner, privacy, sample exam, and licensed-feed behavior.

## Inventory Completeness Checklist

- [x] Reading, example exam, timer/scoring, Tutor, Writing, placeholders, and sample-library management inventoried.
- [x] Success and failure outcomes, persistence boundaries, rights/consent notices, and relevant edge cases included.
- [x] Listening/Speaking are explicitly placeholders; identity/billing are explicitly excluded.
- [x] Requirements use unique sequential REQ-XXX identifiers and are observable/testable.
- [x] Upstream artifacts and source/test evidence are mapped to this inventory.
