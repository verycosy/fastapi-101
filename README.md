[Mastering REST APIs with FastAPI](https://www.udemy.com/course/rest-api-fastapi-python/)

```bash
$ pyenv local 3.11
$ pyenv exec python -v
$ pyenv exec python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ uvicorn socialapi.main:app --reload
$ uvicorn socialapi.main:app --host 0.0.0.0 --port 8001
```

```bash
$ pip install -r requirements-dev.txt
$ pytest
$ pytest -v
$ pytest --fixtures
$ pytest --fixtures-per-test
```

(+ vscode extensions)

- ruff, lint (by rust)
- black, format
- isort, sort import
