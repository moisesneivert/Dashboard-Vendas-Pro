from src.auth import hash_password, verify_password


def test_password_hash_verification():
    password_hash = hash_password("senha-teste")
    assert verify_password("senha-teste", password_hash)
    assert not verify_password("senha-errada", password_hash)