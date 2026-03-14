import { describe, test, expect } from "@jest/globals";
import { Game, SPACE, ADDITION, SUBTRACTION, constructGrid } from "../utils/game.js";

// ---------------------------------------------------------------------------
// Constants — must match backend defaults (routes/solo.py)
// ---------------------------------------------------------------------------

const NUM_ROWS = 6;
const NUM_COLS = 7;
const INCLUDED_OPERATIONS = [ADDITION, SUBTRACTION];
const OPERATOR_SPAWN_RATE = 0.67;
const INCLUDED_DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const GENERATED_TILES_PER_TURN = 2;

// ---------------------------------------------------------------------------
// Canonical game scenarios from backend/tests/conftest.py
// ---------------------------------------------------------------------------

const WON_GAME_1 = {
    seed: "9b4bfe0f-e639-4772-8a40-a5b1f59b5abd",
    moves: ["left", "left", "left", "left", "left", "left", "up", "left", "up", "left", "up", "right", "down", "left", "up", "down", "left", "up", "right", "down", "down", "left", "up", "down", "right", "down", "left", "down", "up", "right", "down", "left", "up", "right", "down", "down", "left", "up", "down", "right", "down", "left", "up", "down", "right", "down", "left", "up", "down", "right", "left", "up", "down", "right", "left", "up", "down", "right", "left", "up", "right", "down", "left", "down", "up", "right", "down", "left", "up", "right", "down", "left", "down", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "up", "down", "down", "left", "up", "right", "down", "down", "left", "right", "up", "down", "left", "up", "right", "down", "down", "left", "up", "right", "down", "left", "down", "up", "left", "up", "right", "down", "left", "up", "right", "down", "left", "down", "up", "right", "down", "left", "up", "right", "down", "down", "right", "down", "right", "up", "left", "up", "down", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "down", "up", "right", "down", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "right", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "right", "down", "left", "up", "right", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "down", "right", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "up", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "down", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "right", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "up", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "up", "right", "down", "left", "up", "right", "left", "right", "left", "right", "left", "right", "up", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "left", "down", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "right", "down", "up", "left", "up", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "right", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "down", "up", "right", "down", "right", "left", "up", "right", "down", "left", "up", "right", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "right", "left", "up", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "up", "left", "right", "up", "down", "up", "left", "right", "down", "left", "up", "right", "down", "left", "down", "up", "down", "right", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "down", "up", "down", "down", "down", "down", "down", "right", "up", "down", "left", "up", "right", "down", "left", "up", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "right", "down", "left", "right", "right", "up", "left", "down", "left", "right", "left", "right", "down", "right", "right", "down", "left", "up", "right", "down", "left", "up", "right", "right", "right", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "left", "up", "left", "down", "left", "up", "left", "up", "right", "down", "left", "up", "right", "down", "down", "right", "down", "up", "right", "down", "left", "up", "left", "down", "right", "down", "left", "up", "right", "down", "left", "down", "right", "left", "up", "right", "up", "up", "up", "down", "left", "up", "right", "up", "right", "right", "right", "up", "up", "up", "right", "up", "up", "right", "right", "up", "right", "up", "right", "up", "right", "right", "left", "right", "up", "left", "up", "right", "right", "right", "up", "right", "up", "right", "right", "right", "right", "right", "left", "up", "up", "up", "up", "up", "up", "up", "right", "down", "up", "right", "up", "up", "right", "right", "right", "right", "right", "up"],
    state: "Won",
};

const WON_GAME_2 = {
    seed: "a223dba4-255a-4659-9228-161d2604e4d6",
    moves: ["left", "up", "right", "left", "down", "left", "right", "left", "right", "left", "right", "up", "down", "left", "up", "left", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "up", "down", "right", "down", "left", "up", "down", "right", "down", "left", "up", "right", "down", "left", "up", "left", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "down", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "right", "down", "left", "up", "left", "right", "left", "right", "up", "down", "down", "left", "up", "right", "down", "left", "right", "up", "down", "left", "up", "right", "down", "right", "left", "up", "up", "down", "left", "right", "up", "down", "left", "right", "down", "up", "left", "up", "right", "left", "right", "up", "down", "up", "left", "down", "up", "down", "left", "right", "down", "right", "right", "up"],
    state: "Won",
};

const LOST_GAME_1 = {
    seed: "66e2f11d-83df-4b05-a3c0-ddda9164194f",
    moves: ["left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "left", "left", "left", "up", "up", "up", "right", "right", "right", "right", "right", "right", "right", "right", "right", "up", "up", "up", "up", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "right", "up", "up", "up", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "up", "up", "up", "up", "up", "down", "down", "down", "up", "up", "up", "right", "right", "right", "right", "left", "left", "up", "up", "up", "up", "up", "up", "up", "up", "up", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "up", "up"],
    state: "Lost",
};

const LOST_GAME_2 = {
    seed: "7a9c52bc-c56e-4443-a0cd-7d6a94280753",
    moves: ["left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "right", "right", "right", "right", "right", "right", "right", "right", "right", "left", "left", "up", "down", "down", "down", "down", "down", "down", "down", "right", "right", "left", "left", "up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "left", "right", "right", "right", "right", "left", "up", "up", "up", "down", "right", "left", "left", "left", "left", "left", "left", "left", "left", "up", "down", "up", "down", "down", "right", "left", "right", "down", "left", "up", "right", "left", "down", "down", "up", "up", "down", "up", "down", "up", "up", "down", "up", "down", "up", "left", "right", "up", "left", "down", "right", "up", "left", "down", "right", "up", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "left", "right", "right", "right", "right", "right", "right", "right", "right", "right", "right", "left", "left", "left", "up", "down", "down", "down", "down", "down", "down", "down", "down", "down", "down", "up", "up", "up", "left", "right", "right", "right", "right", "left", "left", "up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "left", "right", "right", "left", "left", "left", "down", "up", "down", "down", "down", "down", "right", "right", "left", "left", "up", "right", "down", "right", "left", "down", "down"],
    state: "Lost",
};

const ABANDONED_GAME_1 = {
    seed: "68f492cd-26ec-4e92-95f6-219cd79beffc",
    moves: ["up", "down", "left", "right", "up"],
    state: "In Progress",
};

const ABANDONED_GAME_2 = {
    seed: "9f241cb8-55a8-498a-aee0-a39f1523abd4",
    moves: ["left", "up", "right", "down", "up"],
    state: "In Progress",
};

// ---------------------------------------------------------------------------
// replayGame helper
//
// Mirrors the Python build_replay logic in conftest.py:
//   game = construct_game(grid, rng)
//   game.generate_tiles()
//   for move in moves:
//       apply_move(game, move)
//       game.generate_tiles()
// ---------------------------------------------------------------------------

function replayGame(seed, moves) {
    const game = new Game(
        constructGrid(NUM_ROWS, NUM_COLS, SPACE),
        NUM_ROWS,
        NUM_COLS,
        INCLUDED_OPERATIONS,
        OPERATOR_SPAWN_RATE,
        INCLUDED_DIGITS,
        GENERATED_TILES_PER_TURN,
        seed,
    );

    game.generateTiles();

    for (const move of moves) {
        if (move === "up") game.slideUp();
        else if (move === "down") game.slideDown();
        else if (move === "left") game.slideLeft();
        else if (move === "right") game.slideRight();
        else throw new Error(`Unknown move: ${move}`);

        game.generateTiles();
    }

    return game;
}

// ---------------------------------------------------------------------------
// "Big Six" replay suite
// ---------------------------------------------------------------------------

describe("Big Six canonical game replays", () => {
    test.each([
        ["WON_GAME_1", WON_GAME_1],
        ["WON_GAME_2", WON_GAME_2],
        ["LOST_GAME_1", LOST_GAME_1],
        ["LOST_GAME_2", LOST_GAME_2],
        ["ABANDONED_GAME_1", ABANDONED_GAME_1],
        ["ABANDONED_GAME_2", ABANDONED_GAME_2],
    ])("%s reaches expected state", (name, scenario) => {
        const game = replayGame(scenario.seed, scenario.moves);
        expect(game.getState()).toBe(scenario.state);
    });
});
