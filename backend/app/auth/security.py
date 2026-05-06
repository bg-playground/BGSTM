import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


# ---------------------------------------------------------------------------
# Runner-token helpers
# ---------------------------------------------------------------------------

_RUNNER_TOKEN_PREFIX = "bgstm_runner_"


def generate_runner_token() -> str:
    """Generate a new plaintext runner token with the ``bgstm_runner_`` prefix."""
    return _RUNNER_TOKEN_PREFIX + secrets.token_urlsafe(32)


def generate_token_salt() -> str:
    """Generate a fresh 16-byte hex salt for a runner token."""
    return secrets.token_bytes(16).hex()


def hash_runner_token(plaintext: str, salt: str) -> str:
    """Return the salted SHA-256 hex digest of *plaintext*.

    The salt is prepended to the plaintext before hashing so that two tokens
    with identical values produce different digests.
    """
    return hashlib.sha256((salt + plaintext).encode("utf-8")).hexdigest()
