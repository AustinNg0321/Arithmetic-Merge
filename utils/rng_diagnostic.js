#!/usr/bin/env node
// Diagnostic script: DeterministicRNG using FNV-1a seeding + xorshift32.

const SEED = "c52cb2e1-3982-4ab3-988c-523d1f52c6e9";

const FNV_OFFSET = 0x811C9DC5;
const FNV_PRIME  = 0x01000193;

function fnv1a_32(str) {
    // Start with the offset as an unsigned 32-bit value.
    let h = FNV_OFFSET >>> 0;
    for (let i = 0; i < str.length; i++) {
        h = (h ^ str.charCodeAt(i)) >>> 0;
        // Math.imul prevents 64-bit float precision loss during multiplication.
        h = Math.imul(h, FNV_PRIME) >>> 0;
    }
    return h;
}

class DeterministicRNG {
    constructor(seed) {
        this.state = fnv1a_32(seed);
    }

    random() {
        let s = this.state;
        // >>> 0 forces the result to an unsigned 32-bit integer after each shift/xor,
        // matching Python's explicit & 0xFFFFFFFF masking.
        s = (s ^ (s << 13)) >>> 0;
        s = (s ^ (s >>> 17)) >>> 0;  // logical right-shift (>>>), not arithmetic (>>)
        s = (s ^ (s << 5))  >>> 0;
        this.state = s;
        return s / 4294967296.0;
    }
}

const rng = new DeterministicRNG(SEED);
const initState = fnv1a_32(SEED);
console.log(`Seed: ${SEED}`);
console.log(`Initial state (FNV-1a): 0x${initState.toString(16).padStart(8, "0")}`);
console.log();
for (let i = 0; i < 10; i++) {
    const v = rng.random();
    const stateHex = "0x" + rng.state.toString(16).padStart(8, "0");
    console.log(`  [${i}] ${v.toFixed(20)}  (state=${stateHex})`);
}
