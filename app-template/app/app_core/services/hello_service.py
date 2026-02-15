from typing import Optional

_guess_store = {}


def guess_age_for_name(name: str) -> int:
    normalized = name.strip().lower()
    guess = (abs(hash(normalized)) % 43) + 18
    _guess_store[normalized] = guess
    return guess


def get_guess_for_name(name: str) -> Optional[int]:
    return _guess_store.get(name.strip().lower())
