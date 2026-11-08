# Optional sample-exam builder

This folder contains the optional AI-powered command for creating original
sample-exam content and its focused tests. From the project root, run:

```powershell
.\venv\Scripts\python.exe -m sample_exam_builder
```

The builder adds only missing articles to the SQLite sample library. The
Streamlit application reads existing sample articles and questions from the
database and does not import this folder. Removing this folder disables
sample-content generation and its focused tests, but does not prevent the
application from starting or using sample exams already stored in
`data/yki.db`.

The builder uses shared application models, repositories, the database
initializer, and AI client; those modules remain outside this folder because
the application also depends on them.
