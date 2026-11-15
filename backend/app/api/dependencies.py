import hashlib
import hmac
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.session import get_session
from ..models.profile import User

DatabaseSession = Annotated[Session, Depends(get_session)]
basic_auth = HTTPBasic()


def _derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=2**15, r=8, p=3,
        maxmem=64 * 1024**2, dklen=32,
    )


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    return f"scrypt${salt.hex()}${_derive_key(password, salt).hex()}"


def _verify_password(password: str, stored: str | None) -> bool:
    salt, expected = bytes(16), bytes(32)
    valid_hash = False
    if stored:
        try:
            scheme, salt_hex, key_hex = stored.split("$")
            parsed_salt, parsed_key = bytes.fromhex(salt_hex), bytes.fromhex(key_hex)
            if scheme == "scrypt" and len(parsed_salt) == 16 and len(parsed_key) == 32:
                salt, expected = parsed_salt, parsed_key
                valid_hash = True
        except ValueError:
            pass
    matches = hmac.compare_digest(_derive_key(password, salt), expected)
    return valid_hash and matches


def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(basic_auth)],
    session: DatabaseSession,
) -> User:
    user = session.scalar(select(User).where(User.username == credentials.username))
    verified = _verify_password(credentials.password, user.password_hash if user else None)
    if user is None or not verified:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user
