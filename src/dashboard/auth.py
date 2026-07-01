from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 310_000


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    username: str
    name: str
    role: str


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password: str, iterations: int = DEFAULT_ITERATIONS) -> str:
    if len(password) < 8:
        raise ValueError("A senha deve ter pelo menos 8 caracteres.")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return "$".join(
        [
            ALGORITHM,
            str(iterations),
            base64.urlsafe_b64encode(salt).decode().rstrip("="),
            base64.urlsafe_b64encode(digest).decode().rstrip("="),
        ]
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, raw_iterations, raw_salt, raw_digest = encoded.split("$", maxsplit=3)
        if algorithm != ALGORITHM:
            return False
        calculated = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), _decode(raw_salt), int(raw_iterations)
        )
        return hmac.compare_digest(calculated, _decode(raw_digest))
    except (ValueError, TypeError):
        return False


def authenticate(
    username: str, password: str, users: Iterable[Mapping[str, Any]]
) -> AuthenticatedUser | None:
    normalized_username = username.strip().lower()
    for user in users:
        stored_username = str(user.get("username", "")).strip().lower()
        if hmac.compare_digest(normalized_username, stored_username) and verify_password(
            password, str(user.get("password_hash", ""))
        ):
            return AuthenticatedUser(
                username=stored_username,
                name=str(user.get("name", stored_username)),
                role=str(user.get("role", "viewer")),
            )
    return None
