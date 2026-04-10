import secrets
import string


def gen_salt(N: int) -> str:
    return secrets.token_hex(N)
