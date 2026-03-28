from uuid import uuid4


def generate_reference(prefix: str, length: int = 10) -> str:
    token = uuid4().hex[:length].upper()
    if prefix:
        return f"{prefix}-{token}"
    return token
