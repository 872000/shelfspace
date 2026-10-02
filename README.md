# ShelfSpace

![ShelfSpace banner](docs/banner.png)

Your personal library manager: catalog every book you own, lend books to
friends without losing track of them, and build a daily reading habit with
streaks and stats — all in one friendly Django app.

## Features

- **Book catalog** — title, author, ISBN, page count, and reading status
  (to read / reading / finished)
- **Offline ISBN lookup** — type an ISBN and the app resolves it from a
  bundled local catalog (`library/isbn_catalog.json`). **Zero network calls,
  no API keys, no secrets** — unknown ISBNs fall back to quick manual entry
- **Lending tracker** — lend a book to a friend with a due date; the app
  blocks double-lending, and shows active loans plus an **overdue list**
- **Reading stats** — books finished per month, total pages read, current
  reading streak (consecutive days), all on the dashboard
- **REST API** — CRUD for books, loans, and reading logs; `GET /api/isbn/?isbn=...`
  for the offline lookup; `GET /api/loans/overdue/`; `GET /api/stats/` for the
  full dashboard summary; `POST /api/loans/<id>/mark_returned/`
- **Server-rendered UI** — dashboard with stat cards, book list with status
  filters, book detail with lend/log/mark-finished actions, loan management
  page, reading log page
- **100% offline** — SQLite, no external services

## How to run

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000 — the browsable API lives at http://127.0.0.1:8000/api/.

## How to test

```bash
pytest
```

## Tech stack

Python · Django · Django REST Framework · SQLite · pytest / pytest-django
