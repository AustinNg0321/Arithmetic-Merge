#!/usr/bin/env node
/**
 * Divergence diagnostic — JavaScript side.
 *
 * 1. Run to get per-step sums:
 *        node divergence_diagnostic.mjs > js_steps.txt
 *
 * 2. Compare with the Python output:
 *        python3 divergence_diagnostic.py > py_steps.txt
 *        diff py_steps.txt js_steps.txt
 *
 * 3. Set BREAK_INDEX to the first differing step for a detailed snapshot.
 *
 * Output format (one line per step, machine-diffable):
 *     step|dir|sum_after_move|sum_after_spawn|rng_state_after_spawn
 *
 * Imports the real frontend/utils/game.js so there is zero translation risk.
 */

import { Game, constructGrid, SPACE, ADDITION, SUBTRACTION } from "../frontend/utils/game.js";

// ── Configure ─────────────────────────────────────────────────────────────────
const SEED  = "47901452-df64-40c5-beb7-417249808f3f";      // e.g. "c52cb2e1-3982-4ab3-988c-523d1f52c6e9"
const MOVES = ["left","up","left","left","left","up","left","up","down","up","left","left","up","left","up","right","down","left","up","down","right","down","left","down","up","down","right","left","up","down","right","down","left","up","right","down","down","left","up","right","down","down","left","up","left","down","up","left","down","up","right","down","left","down","up","right","down","left","up","down","left","up","down","left","up","right","left","down","up","up","right","down","left","up","right","down","left","up","right","down","left","up","right","down","left","right","down","left","up","right","down","up","left","left","up","up","up","up","up","up","up","up","up","left","down","left","right","left","up","left","right","up","up","up","left","up","up","right","down","up","left","right","left","up","down","left","right","down","left","right","left","up","right","down","left","up","right","down","left","up","right","down","left","up","right","down","left","up","right","down","left","up","right","down","left","up","right","down","down","down","right","left","up","right","down","left","up","right","down","left"];
const BREAK_INDEX = null; // set to an int to print a detailed snapshot at that step index
// ─────────────────────────────────────────────────────────────────────────────

const NUM_ROWS  = 6;
const NUM_COLS  = 7;
const OPS       = [ADDITION, SUBTRACTION];
const OP_RATE   = 0.67;
const DIGITS    = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const TILES_PER = 2;
const OPERATORS = new Set(OPS);


function boardSum(grid) {
    let total = 0;
    for (const row of grid) {
        for (const cell of row) {
            if (cell !== SPACE && !OPERATORS.has(cell)) {
                total += Number(cell);
            }
        }
    }
    return total;
}

function deepCopyGrid(grid) {
    return grid.map(row => [...row]);
}

function rngState(game) {
    // Access private _rng._state via the backing field name mangling.
    // DeterministicRNG stores state as _state (no JS private field name mangling
    // because the class is not exported — we reach it through the Game instance).
    return "0x" + game._rng._state.toString(16).padStart(8, "0");
}

function printGrid(grid, label = "") {
    if (label) process.stdout.write(`  [${label}]\n`);
    for (const row of grid) {
        process.stdout.write("  " + row.map(c => String(c).padStart(5)).join("") + "\n");
    }
    process.stdout.write("\n");
}

function printSnapshot(step, direction, beforeMove, afterMove, afterSpawn) {
    process.stdout.write(`\n╔══ SNAPSHOT  step=${step}  dir=${direction} ══╗\n`);
    printGrid(beforeMove, "board before move");
    printGrid(afterMove,  "board after move (before spawn)");
    printGrid(afterSpawn, "board after spawn");

    const spawned = [];
    for (let r = 0; r < NUM_ROWS; r++) {
        for (let c = 0; c < NUM_COLS; c++) {
            if (afterMove[r][c] === SPACE && afterSpawn[r][c] !== SPACE) {
                spawned.push([r, c, afterSpawn[r][c]]);
            }
        }
    }
    process.stdout.write(`  Spawned tiles : ${JSON.stringify(spawned)}\n`);

    const changed = [];
    for (let r = 0; r < NUM_ROWS; r++) {
        for (let c = 0; c < NUM_COLS; c++) {
            if (beforeMove[r][c] !== afterMove[r][c]) {
                changed.push([r, c, beforeMove[r][c], "→", afterMove[r][c]]);
            }
        }
    }
    process.stdout.write(`  Changed cells : ${JSON.stringify(changed)}\n\n`);
}


// ── Main ──────────────────────────────────────────────────────────────────────
const game = new Game(
    constructGrid(NUM_ROWS, NUM_COLS, SPACE),
    NUM_ROWS, NUM_COLS,
    OPS, OP_RATE, DIGITS, TILES_PER,
    SEED,
);
game.generateTiles();

process.stdout.write(`seed=${SEED}\n`);
process.stdout.write(`init_sum=${boardSum(game.getGame())}  init_rng=${rngState(game)}\n\n`);
process.stdout.write("step|dir|sum_after_move|sum_after_spawn|rng_state_after_spawn\n");

for (let i = 0; i < MOVES.length; i++) {
    const move = MOVES[i];
    const gridBeforeMove = deepCopyGrid(game.getGame());

    switch (move) {
        case "up":    game.slideUp();    break;
        case "down":  game.slideDown();  break;
        case "left":  game.slideLeft();  break;
        case "right": game.slideRight(); break;
        default:
            process.stderr.write(`UNKNOWN MOVE at step ${i}: ${JSON.stringify(move)}\n`);
            process.exit(1);
    }

    const sumAfterMove  = boardSum(game.getGame());
    const gridAfterMove = deepCopyGrid(game.getGame());

    game.generateTiles();

    const sumAfterSpawn  = boardSum(game.getGame());
    const gridAfterSpawn = deepCopyGrid(game.getGame());
    const stateHex       = rngState(game);

    process.stdout.write(`${i}|${move}|${sumAfterMove}|${sumAfterSpawn}|${stateHex}\n`);

    if (BREAK_INDEX !== null && i === BREAK_INDEX) {
        printSnapshot(i, move, gridBeforeMove, gridAfterMove, gridAfterSpawn);
        break;
    }
}

process.stdout.write(`\nfinal_state=${game.getState()}\n`);
