from src.dashboard.auth import authenticate, hash_password, verify_password


def test_hash_and_verify_password():
    encoded = hash_password("Senha@123")
    assert verify_password("Senha@123", encoded)
    assert not verify_password("incorreta", encoded)


def test_hash_rejects_short_password():
    try:
        hash_password("123")
    except ValueError as exc:
        assert "8 caracteres" in str(exc)
    else:
        raise AssertionError("ValueError expected")


def test_authenticate_returns_user():
    users = [
        {
            "username": "admin",
            "name": "Admin",
            "role": "admin",
            "password_hash": hash_password("Senha@123"),
        }
    ]
    user = authenticate("ADMIN", "Senha@123", users)
    assert user is not None
    assert user.role == "admin"


def test_authenticate_rejects_invalid_password():
    users = [{"username": "admin", "password_hash": hash_password("Senha@123")}]
    assert authenticate("admin", "errada", users) is None
