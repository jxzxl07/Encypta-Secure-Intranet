# Architecture

Encrypta is organized around a small set of layers:

- `main.py` starts the application and ensures the SQLite database exists.
- `src/config.py` centralizes project paths and the admin server IP.
- `src/database/` owns schema creation and database helpers.
- `src/crypto/` contains the educational hashing and encryption implementations.
- `src/network/` contains socket servers and audio/video worker threads.
- `src/ui/` contains PyQt windows split into auth, dashboard, chat, and call screens.
- `src/utils/` contains validation and LAN helper functions.

The UI modules keep navigation imports either one-way or local to a click handler so feature modules can stay focused without import loops.

## Runtime Data

The local SQLite database is created at `encrypta.db` in the project root. It is intentionally ignored by Git.
