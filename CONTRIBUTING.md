# Contributing

Thanks for improving Encrypta.

## Local Checks

Run these before opening a pull request:

```bash
python -m compileall main.py src scripts
python scripts/create_db.py
```

## Style

- Keep UI code inside `src/ui/`.
- Keep reusable database setup in `src/database/`.
- Keep socket and media worker code in `src/network/`.
- Avoid committing `encrypta.db`, `.env`, virtual environments, or generated cache files.
