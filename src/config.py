"""Project-wide paths and runtime configuration."""

from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
DB_PATH = PROJECT_ROOT / "encrypta.db"

# Override this on another machine with ENCRYPTA_SERVER_IP=192.168.x.x.
SERVER_IP = os.getenv("ENCRYPTA_SERVER_IP", "127.0.0.1")
EMAIL_ADDRESS = os.getenv("ENCRYPTA_EMAIL_ADDRESS", "")
EMAIL_APP_PASSWORD = os.getenv("ENCRYPTA_EMAIL_APP_PASSWORD", "")
ADMIN_USERNAME = os.getenv("ENCRYPTA_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ENCRYPTA_ADMIN_PASSWORD", "adminpassword")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


STATUS_SERVER_PORT = _env_int("ENCRYPTA_STATUS_SERVER_PORT", 5000)
CONNECTION_PORT = _env_int("ENCRYPTA_CONNECTION_PORT", 5001)
DIRECT_MESSAGE_PORT = _env_int("ENCRYPTA_DIRECT_MESSAGE_PORT", 5002)
DIRECT_FILE_PORT = _env_int("ENCRYPTA_DIRECT_FILE_PORT", 5003)
GROUP_PORT = _env_int("ENCRYPTA_GROUP_PORT", 5004)
CALL_SIGNAL_PORT = _env_int("ENCRYPTA_CALL_SIGNAL_PORT", 5005)
CALL_AUDIO_PORT = _env_int("ENCRYPTA_CALL_AUDIO_PORT", 5006)
VIDEO_SIGNAL_PORT = _env_int("ENCRYPTA_VIDEO_SIGNAL_PORT", 5007)


def asset_path(filename: str) -> str:
    return str(ASSETS_DIR / filename)
