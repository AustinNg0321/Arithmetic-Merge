#!/usr/bin/env python3
"""Diagnostic script: DeterministicRNG using FNV-1a seeding + xorshift32."""

SEED = "c52cb2e1-3982-4ab3-988c-523d1f52c6e9"

FNV_OFFSET = 0x811C9DC5
FNV_PRIME  = 0x01000193


def fnv1a_32(data: str) -> int:
    h = FNV_OFFSET
    for byte in data.encode("utf-8"):
        h ^= byte
        h = (h * FNV_PRIME) & 0xFFFFFFFF
    return h


class DeterministicRNG:
    def __init__(self, seed: str):
        self.state = fnv1a_32(seed)

    def random(self) -> float:
        s = self.state
        s ^= (s << 13) & 0xFFFFFFFF
        s ^= (s >> 17) & 0xFFFFFFFF
        s ^= (s <<  5) & 0xFFFFFFFF
        self.state = s
        return s / 4294967296.0


rng = DeterministicRNG(SEED)
print(f"Seed: {SEED}")
print(f"Initial state (FNV-1a): {fnv1a_32(SEED):#010x}")
print()
for i in range(10):
    v = rng.random()
    print(f"  [{i}] {v:.20f}  (state={rng.state:#010x})")
