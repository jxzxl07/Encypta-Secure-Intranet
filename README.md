# Encrypta Secure Intranet

Encrypta is a PyQt5 desktop app for encrypted LAN messaging, group chats, and audio/video calls. The project was refactored from a single large backup file into a small Python package with separate UI, database, cryptography, networking, and utility modules.

## Features

- User sign-up and login with email-based 2FA
- Local SQLite database initialization
- Direct messages and group chats
- Custom educational RSA-style asymmetric encryption
- Custom educational symmetric block encryption
- Audio and video calling over local network sockets
- Admin dashboard for online user status updates

> This project is educational. The custom cryptography is not production-grade and should not be used to protect real secrets.

## Project Structure

```text
.
├── assets/                  # UI images and app icon
├── docs/                    # Architecture notes
├── scripts/
│   └── create_db.py         # Database initialization script
├── src/
│   ├── config.py            # Project paths and environment config
│   ├── crypto/              # Hashing and encryption helpers
│   ├── database/            # SQLite schema and database helpers
│   ├── network/             # Status, call, audio, and video socket workers
│   ├── ui/                  # PyQt windows split by feature area
│   └── utils/               # Validation, IP, and status helpers
├── main.py                  # Application entry point
├── requirements.txt
└── createDB.py              # Backwards-compatible DB setup wrapper
```

## Setup

1. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

On some systems, `pyaudio` needs PortAudio installed first.

3. Create the local database.

```bash
python scripts/create_db.py
```

4. Run the app.

```bash
python main.py
```

## Configuration

The admin status server IP defaults to `127.0.0.1`. Set it before launching clients on another machine:

```bash
export ENCRYPTA_SERVER_IP=192.168.1.100
python main.py
```

Email 2FA uses environment variables. If these are not set, the app shows a local development code in the verification dialog.

```bash
export ENCRYPTA_EMAIL_ADDRESS=your_email@example.com
export ENCRYPTA_EMAIL_APP_PASSWORD=your_app_password
```

Admin credentials can also be overridden:

```bash
export ENCRYPTA_ADMIN_USERNAME=admin
export ENCRYPTA_ADMIN_PASSWORD=change-this
```

Default local ports are separated by feature and can be overridden if your machine already uses one of them:

```text
5000 status server
5001 connection requests
5002 direct messages
5003 direct file transfer
5004 group chat notifications
5005 call signaling
5006 call audio
5007 video signaling/streaming
```

The app stores its local SQLite database at `encrypta.db` in the project root. That file is ignored by Git.

## Admin Login

```text
Username: admin
Password: adminpassword
```

These are the default development credentials. For shared machines, override them with the environment variables above.

## Developer Checks

```bash
python -m compileall main.py src scripts
python scripts/create_db.py
```

## License

MIT
