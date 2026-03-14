import { describe, test, expect } from "@jest/globals";
import { Game, SPACE, ADDITION, SUBTRACTION, constructGrid } from "../utils/game.js";

// ---------------------------------------------------------------------------
// Task 1 — RNG Ground Truth
//
// Python ground truth:
//   from utils.game import DeterministicRNG
//   rng = DeterministicRNG("parity-seed")
//   print([rng.random() for _ in range(5)])
// => [0.8087789723649621, 0.14422997692599893, 0.20571449282579124, 0.27728989161551, 0.9680565930902958]
//
// The JS DeterministicRNG is private, but we can reach it by observing
// tile generation, which consumes the RNG identically to the Python code.
// Instead, we expose it by subclassing Game and reading `this._rng`.
// ---------------------------------------------------------------------------

// Reach into the private RNG by extending Game so we can call _rng.random()
// directly — this avoids any need to export DeterministicRNG.
class InspectableGame extends Game {
    getRng() {
        return this._rng;
    }
}

const NUM_ROWS = 6;
const NUM_COLS = 7;

function makeInspectable(seed) {
    return new InspectableGame(
        constructGrid(NUM_ROWS, NUM_COLS, SPACE),
        NUM_ROWS,
        NUM_COLS,
        [ADDITION, SUBTRACTION],
        0.67,
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        2,
        seed,
    );
}

describe("DeterministicRNG parity with Python", () => {
    test("first 5 random() values for 'parity-seed' match Python output", () => {
        const game = makeInspectable("parity-seed");
        const rng = game.getRng();

        const results = [rng.random(), rng.random(), rng.random(), rng.random(), rng.random()];

        expect(results[0]).toBeCloseTo(0.8087789723649621, 10);
        expect(results[1]).toBeCloseTo(0.14422997692599893, 10);
        expect(results[2]).toBeCloseTo(0.20571449282579124, 10);
        expect(results[3]).toBeCloseTo(0.27728989161551, 10);
        expect(results[4]).toBeCloseTo(0.9680565930902958, 10);
    });
});
