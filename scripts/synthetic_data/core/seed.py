from __future__ import annotations

import hashlib
import random


class SeedFactory:
    def __init__(self, master_seed: int) -> None:
        self._master_seed = master_seed

    def rng(self, *context: str) -> random.Random:
        payload = "\x1f".join((str(self._master_seed), *context))
        digest = hashlib.sha256(payload.encode("utf-8")).digest()
        return random.Random(int.from_bytes(digest[:16], byteorder="big"))
