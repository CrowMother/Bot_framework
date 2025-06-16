# AGENTS.md

This file guides Codex in writing code for our Python library.

---

## 🗂️ Project Structure

- `/src/<package>` – main library code  
- `/tests` – pytest-compatible test files (named `test_*.py`)  
- `setup.py` or `pyproject.toml` – packaging / install config  
- `README.md`, `LICENSE`, `CONTRIBUTING.md` – documentation and contribution etiquette  
- `.gitignore`, `.pre-commit-config.yaml` – linting, formatting, and environment ignores  

Adhere to the layout of modern templates like **cshmookler/py_template** :contentReference[oaicite:1]{index=1}.

---

## 🧹 Coding Conventions

- Language: **Python 3.8+**
- Follow PEP8; auto-format with **Black**; lint with **flake8**
- Include clear docstrings (Google or numpydoc style)
- Keep code modular: small, testable functions
- Use fixtures (`@pytest.fixture`) with `yield` for setup/teardown :contentReference[oaicite:2]{index=2}

---

## ⚙️ Development Workflow

1. Install dev dependencies:
   ```bash
   pip install -e .[dev]   
   ```
