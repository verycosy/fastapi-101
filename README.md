$ pyenv local 3.11
$ pyenv exec python -v
$ pyenv exec python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ uvicorn social-api.main:app --reload

(+ vscode extensions)
ruff - lint (by rust)
black - format
isort - sort import

$ pip install -r requirements-dev.txt
