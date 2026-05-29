# CV-Craft-Studio: Streamlit Cloud Deployment Checklist

Use this checklist if Streamlit Cloud shows: `Get http://localhost:8501/healthz: connect: connection refused`.

That message usually means the app process did not start. The most common reasons are an incorrect main file path, missing root-level requirements, missing Python runtime, or a dependency installation/startup error.

## Required repository structure

At the root of the GitHub repository, you should see:

```text
app.py
requirements.txt
runtime.txt
README.md
.streamlit/config.toml
assets/
modules/
samples/
tests/
```

Do not upload only the ZIP file to GitHub. Extract it and push the project files.

## Streamlit Cloud settings

- Repository: `dr-alok-tiwari/CV-Craft-Studio`
- Branch: `main`
- Main file path: `app.py`

If your files are inside an extra folder named `CV-Craft-Studio`, then set the main file path to:

```text
CV-Craft-Studio/app.py
```

Better option: move all files from that inner folder to the repository root.

## Runtime

`runtime.txt` must be at the repository root and must contain:

```text
python-3.11
```

## Local test before pushing

```bash
pip install -r requirements.txt
python verify.py
python -m pytest tests/ -q
streamlit run app.py --server.headless=true
```

Open this in another terminal:

```bash
curl http://localhost:8501/healthz
```

Expected output:

```text
ok
```

## If deployment still fails

Open Streamlit Cloud -> Manage app -> Logs -> copy the full Python traceback. The health-check line alone is not enough to identify the exact crash.
