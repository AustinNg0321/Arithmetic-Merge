import { describe, test, expect } from "@jest/globals";
import {
  Game,
  SPACE,
  ADDITION,
  SUBTRACTION,
  OPERATORS,
  constructGrid,
  evaluate,
  removeExtraSpaces,
  collapseOperators,
  collapseListLeft,
  collapseListRight,
  outOfBounds,
} from "../utils/game.js";

const NUM_ROWS = 6;
const NUM_COLS = 7;
const INCLUDED_OPERATIONS = [ADDITION, SUBTRACTION];
const OPERATOR_SPAWN_RATE = 0.67;
const INCLUDED_DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const GENERATED_TILES_PER_TURN = 2;
const DEFAULT_SEED = "test-seed";

const EMPTY_GRID = [
  [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
  [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
  [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
  [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
  [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
  [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
];

const NO_OPERATIONS_GRID = [
  [1, SPACE, 2],
  [SPACE, 3, SPACE],
  [4, 5, SPACE],
];

const ALREADY_WON_GRID = [
  [1, 2, 3, 4, 5, 6, 7],
  [8, 9, 10, 11, 12, 13, 14],
  [15, 16, 17, 18, 19, 20, 21],
  [22, 23, 24, 25, 26, 27, 28],
  [29, 30, 31, 32, 33, 34, 35],
  [36, 37, 38, 39, 40, 41, 67],
];

const ALREADY_LOST_GRID = [
  [1001, 1001, 1001, 1001, 1001, 1001, 1001],
  [1001, 1001, 1001, 1001, 1001, 1001, 1001],
  [1001, 1001, 1001, 1001, 1001, 1001, 1001],
  [1001, 1001, 1001, 1001, 1001, 1001, 1001],
  [1001, 1001, 1001, 1001, 1001, 1001, 1001],
  [1001, 1001, 1001, 1001, 1001, 1001, 1001],
];

const FULL_BUT_NOT_LOST_GRID = [
  [1, ADDITION, 3, SUBTRACTION, 5, ADDITION, 7],
  [8, SUBTRACTION, 10, ADDITION, 12, SUBTRACTION, 14],
  [15, ADDITION, 17, SUBTRACTION, 19, ADDITION, 21],
  [22, SUBTRACTION, 24, ADDITION, 26, SUBTRACTION, 28],
  [29, ADDITION, 31, SUBTRACTION, 33, ADDITION, 35],
  [36, SUBTRACTION, 38, ADDITION, 40, SUBTRACTION, 42],
];

const GOT_67_BUT_NO_MOVES_GRID = [
  [67, 1],
  [1, 1001],
];

function cloneGrid(grid) {
  return grid.map((row) => [...row]);
}

function makeGame(grid, seed = DEFAULT_SEED) {
  const game = new Game(
    cloneGrid(grid),
    grid.length,
    grid[0].length,
    INCLUDED_OPERATIONS,
    OPERATOR_SPAWN_RATE,
    INCLUDED_DIGITS,
    GENERATED_TILES_PER_TURN,
    seed,
  );
  game.updateBlankSpaces();
  return game;
}

function blankSpaceSet(grid) {
  const out = new Set();
  for (let i = 0; i < grid.length; i += 1) {
    for (let j = 0; j < grid[0].length; j += 1) {
      if (grid[i][j] === SPACE) {
        out.add(`${i},${j}`);
      }
    }
  }
  return out;
}

function assertBlankSpacesConsistent(game) {
  const boardBlanks = blankSpaceSet(game.getGame());
  const trackedBlanks = new Set(game.getBlankSpaces().map(([r, c]) => `${r},${c}`));
  expect(trackedBlanks).toEqual(boardBlanks);
}

function applyMoves(game, moves) {
  for (const move of moves) {
    if (move === "up") game.slideUp();
    else if (move === "down") game.slideDown();
    else if (move === "left") game.slideLeft();
    else if (move === "right") game.slideRight();
    else throw new Error(`Unknown move: ${move}`);
  }
}

describe("utility behaviors (ported from test_game_util.py)", () => {
  test("constructGrid builds expected dimensions", () => {
    expect(constructGrid(2, 3, 0)).toEqual([
      [0, 0, 0],
      [0, 0, 0],
    ]);
  });

  test("evaluate supports addition and subtraction", () => {
    expect(evaluate(3, ADDITION, 4)).toBe(7);
    expect(evaluate(10, SUBTRACTION, 6)).toBe(4);
  });

  test("evaluate rejects invalid operator", () => {
    expect(() => evaluate(1, "/", 2)).toThrow("Invalid operator");
  });

  test("removeExtraSpaces removes only SPACE entries", () => {
    expect(removeExtraSpaces([SPACE, 1, ADDITION, SPACE, 2, SPACE])).toEqual([1, ADDITION, 2]);
  });

  test("collapseOperators de-duplicates adjacent operators", () => {
    expect(collapseOperators([1, ADDITION, ADDITION, SUBTRACTION, SUBTRACTION, 2], OPERATORS)).toEqual([
      1,
      ADDITION,
      SUBTRACTION,
      2,
    ]);
  });

  test("collapseListLeft reduces left-to-right", () => {
    expect(collapseListLeft([1, ADDITION, ADDITION, 2, ADDITION, 3])).toEqual([3, ADDITION, 3]);
  });

  test("collapseListRight reduces right-to-left", () => {
    expect(collapseListRight([1, ADDITION, ADDITION, 2, ADDITION, 3])).toEqual([1, ADDITION, 5]);
  });

  test("outOfBounds ignores spaces/operators and detects numeric overflow", () => {
    expect(outOfBounds([[SPACE, ADDITION], [SUBTRACTION, SPACE]])).toBe(false);
    expect(outOfBounds([[1001]])).toBe(true);
  });
});

describe("game behaviors (ported from test_game.py)", () => {
  test("empty game tracks blank spaces and tile generation consumes blanks", () => {
    const game = makeGame(EMPTY_GRID);
    expect(game.getBlankSpaces().length).toBe(42);
    assertBlankSpacesConsistent(game);

    game.generateTiles();
    expect(game.getBlankSpaces().length).toBe(42 - game.getNumGeneratedTilesPerTurn());
    assertBlankSpacesConsistent(game);
  });

  test("movement without operators works in all directions", () => {
    const game = makeGame(NO_OPERATIONS_GRID);

    const leftGame = makeGame(NO_OPERATIONS_GRID);
    leftGame.slideLeft();
    expect(leftGame.getGame()).toEqual([
      [1, 2, SPACE],
      [3, SPACE, SPACE],
      [4, 5, SPACE],
    ]);

    const rightGame = makeGame(NO_OPERATIONS_GRID);
    rightGame.slideRight();
    expect(rightGame.getGame()).toEqual([
      [SPACE, 1, 2],
      [SPACE, SPACE, 3],
      [SPACE, 4, 5],
    ]);

    const upGame = makeGame(NO_OPERATIONS_GRID);
    upGame.slideUp();
    expect(upGame.getGame()).toEqual([
      [1, 3, 2],
      [4, 5, SPACE],
      [SPACE, SPACE, SPACE],
    ]);

    const downGame = makeGame(NO_OPERATIONS_GRID);
    downGame.slideDown();
    expect(downGame.getGame()).toEqual([
      [SPACE, SPACE, SPACE],
      [1, 3, SPACE],
      [4, 5, 2],
    ]);

    expect(new Set(game.getValidMoves())).toEqual(new Set(["up", "down", "left", "right"]));
    expect(game.isWon()).toBe(false);
    expect(game.isLost()).toBe(false);
  });

  test("already won board remains static with no valid moves", () => {
    const game = makeGame(ALREADY_WON_GRID);
    applyMoves(game, ["up", "down", "left", "right"]);
    expect(game.getGame()).toEqual(ALREADY_WON_GRID);
    expect(game.getValidMoves()).toEqual([]);
    expect(game.isWon()).toBe(true);
    expect(game.isLost()).toBe(false);
  });

  test("already lost board remains static with no valid moves", () => {
    const game = makeGame(ALREADY_LOST_GRID);
    applyMoves(game, ["up", "down", "left", "right"]);
    expect(game.getGame()).toEqual(ALREADY_LOST_GRID);
    expect(game.getValidMoves()).toEqual([]);
    expect(game.isLost()).toBe(true);
    expect(game.isWon()).toBe(false);
  });

  test("full-but-not-lost board only allows left/right and remains in progress", () => {
    const game = makeGame(FULL_BUT_NOT_LOST_GRID);
    expect(game.getBlankSpaces()).toHaveLength(0);

    const upGame = makeGame(FULL_BUT_NOT_LOST_GRID);
    upGame.slideUp();
    expect(upGame.getGame()).toEqual(FULL_BUT_NOT_LOST_GRID);

    const downGame = makeGame(FULL_BUT_NOT_LOST_GRID);
    downGame.slideDown();
    expect(downGame.getGame()).toEqual(FULL_BUT_NOT_LOST_GRID);

    const leftGame = makeGame(FULL_BUT_NOT_LOST_GRID);
    leftGame.slideLeft();
    expect(leftGame.getGame()).toEqual([
      [4, SUBTRACTION, 12, SPACE, SPACE, SPACE, SPACE],
      [-2, ADDITION, -2, SPACE, SPACE, SPACE, SPACE],
      [32, SUBTRACTION, 40, SPACE, SPACE, SPACE, SPACE],
      [-2, ADDITION, -2, SPACE, SPACE, SPACE, SPACE],
      [60, SUBTRACTION, 68, SPACE, SPACE, SPACE, SPACE],
      [-2, ADDITION, -2, SPACE, SPACE, SPACE, SPACE],
    ]);

    const rightGame = makeGame(FULL_BUT_NOT_LOST_GRID);
    rightGame.slideRight();
    expect(rightGame.getGame()).toEqual([
      [SPACE, SPACE, SPACE, SPACE, 4, SUBTRACTION, 12],
      [SPACE, SPACE, SPACE, SPACE, -2, ADDITION, -2],
      [SPACE, SPACE, SPACE, SPACE, 32, SUBTRACTION, 40],
      [SPACE, SPACE, SPACE, SPACE, -2, ADDITION, -2],
      [SPACE, SPACE, SPACE, SPACE, 60, SUBTRACTION, 68],
      [SPACE, SPACE, SPACE, SPACE, -2, ADDITION, -2],
    ]);

    expect(new Set(game.getValidMoves())).toEqual(new Set(["left", "right"]));
    expect(game.isWon()).toBe(false);
    expect(game.isLost()).toBe(false);
  });

  test("67 present with no moves is won and not lost", () => {
    const game = makeGame(GOT_67_BUT_NO_MOVES_GRID);
    applyMoves(game, ["up", "down", "left", "right"]);
    expect(game.getGame()).toEqual(GOT_67_BUT_NO_MOVES_GRID);
    expect(game.getValidMoves()).toEqual([]);
    expect(game.isWon()).toBe(true);
    expect(game.isLost()).toBe(false);
  });

  test("win/lose edge conditions", () => {
    expect(makeGame([[67]]).isWon()).toBe(true);
    expect(makeGame([[66]]).isWon()).toBe(false);
    expect(makeGame([[1, 2]]).isLost([])).toBe(true);
    expect(makeGame([[2000]]).isLost(["left"])).toBe(true);
    expect(makeGame([[1, SPACE]]).isLost()).toBe(false);
  });
});

describe("determinism and move encoding", () => {
  test("same seed + same move sequence => identical board/state", () => {
    const seed = "repro-seed-123";
    const moves = ["up", "left", "down", "right", "up", "left"];

    const g1 = makeGame(EMPTY_GRID, seed);
    const g2 = makeGame(EMPTY_GRID, seed);

    for (const move of moves) {
      g1.generateTiles();
      g2.generateTiles();
      applyMoves(g1, [move]);
      applyMoves(g2, [move]);
    }

    expect(g1.getGame()).toEqual(g2.getGame());
    expect(g1.getState()).toBe(g2.getState());
    expect(g1.getBlankSpaces()).toEqual(g2.getBlankSpaces());
  });

  test("different seeds diverge for tile generation", () => {
    const g1 = makeGame(EMPTY_GRID, "seed-a");
    const g2 = makeGame(EMPTY_GRID, "seed-b");

    g1.generateTiles();
    g2.generateTiles();

    expect(g1.getGame()).not.toEqual(g2.getGame());
  });
});
