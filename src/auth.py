import base64
import hashlib
import hmac
from typing import Any


def hash_password(password: str, salt: bytes | None = None, iterations: int = 390_000) -> str:
    """
    Gera hash PBKDF2 para senha.
    Formato: pbkdf2_sha256$iterations$salt_base64$hash_base64
    """
    if salt is None:
        salt = hashlib.sha256(password.encode("utf-8")).digest()[:16]

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )

    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def get_users_from_secrets(st_secrets: Any) -> dict:
    """
    Lê usuários do st.secrets.
    Esperado:
    [auth.users.admin]
    name = "Administrador"
    password_hash = "..."
    role = "admin"
    """
    try:
        users = st_secrets["auth"]["users"]
        return {username: dict(config) for username, config in users.items()}
    except Exception:
        return {}