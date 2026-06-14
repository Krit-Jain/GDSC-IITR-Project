# Contributing to Nexvara

Thank you for your interest in contributing to **Nexvara**! 🎉

---

## 🚀 Getting Started

1. **Fork** the repository and clone your fork locally.
2. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes following the conventions below.
4. Push your branch and open a **Pull Request** against `main`.

---

## 📁 Project Structure

| Directory | Purpose |
|---|---|
| `backend/` | Python FastAPI backend — AST engine, metrics, AI service |
| `frontend/` | React + Vite frontend — React Flow canvas, UI components |
| `docs/` | Architecture docs, design notes |

See [docs/architecture.md](docs/architecture.md) for a detailed system overview.

---

## 🧹 Code Style

### Backend (Python)
- Follow **PEP 8** style conventions
- Use **type hints** on all function signatures
- Docstrings on all public functions (Google style)
- Run `black` for formatting and `flake8` for linting

### Frontend (JavaScript/React)
- Use **functional components** with hooks only
- Component files: `PascalCase.jsx`
- Utility files: `camelCase.js`
- CSS: vanilla CSS with CSS variables (no inline styles)

---

## 🧪 Testing

- Backend tests go in `backend/tests/`
- Run: `pytest backend/tests/`

---

## 🐛 Reporting Issues

Open a GitHub Issue with:
- A clear title
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if UI-related)

---

## 📋 Commit Message Convention

Use **Conventional Commits**:

```
feat: add blast radius analysis endpoint
fix: resolve circular import detection bug
docs: update architecture diagram
refactor: extract AST engine into service layer
```

---

*Happy building! 🔍*
