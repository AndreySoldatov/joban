import random
import string


def gen_salt(N: int) -> str:
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))
