// Constants for operations - NEED TO CHANGE IF CHANGING THE MAXIMUM/MINIMUM VALUES
export const ADDITION = "+";
export const SUBTRACTION = "-";
export const MULTIPLICATION = "*";
export const SPACE = " ";
export const OPERATORS = [ADDITION, SUBTRACTION];

class DeterministicRNG {
  constructor(seed) {
    this._state = this.#hashSeed(seed);
    if (this._state === 0) {
      this._state = 0x6d2b79f5;
    }
  }

  #hashSeed(seed) {
    const text = seed == null ? "" : String(seed);
    const bytes = new TextEncoder().encode(text);
    let hash = 0x811c9dc5;
    for (const b of bytes) {
      hash ^= b;
      hash = Math.imul(hash, 0x01000193) >>> 0;
    }
    return hash >>> 0;
  }

  #nextUint32() {
    let x = this._state >>> 0;
    x ^= (x << 13) >>> 0;
    x ^= x >>> 17;
    x ^= (x << 5) >>> 0;
    this._state = x >>> 0;
    return this._state;
  }

  random() {
    return this.#nextUint32() / 4294967296;
  }

  choice(sequence) {
    if (sequence.length === 0) {
      throw new Error("Cannot choose from an empty sequence");
    }
    const idx = Math.floor(this.random() * sequence.length);
    return sequence[idx];
  }

  sample(population, k) {
    const items = [...population];
    if (k < 0 || k > items.length) {
      throw new Error("Sample larger than population or is negative");
    }
    for (let i = items.length - 1; i > 0; i -= 1) {
      const j = Math.floor(this.random() * (i + 1));
      [items[i], items[j]] = [items[j], items[i]];
    }
    return items.slice(0, k);
  }
}

export function constructGrid(numRows, numCols, item) {
  return Array.from({ length: numRows }, () => Array.from({ length: numCols }, () => item));
}

export function evaluate(num1, operator, num2) {
  if (operator === ADDITION) {
    return num1 + num2;
  }
  if (operator === SUBTRACTION) {
    return num1 - num2;
  }
  if (operator === MULTIPLICATION) {
    return num1 * num2;
  }
  throw new Error("Invalid operator: operator must be +, -, or *");
}

export function removeExtraSpaces(list) {
  return list.filter((item) => item !== SPACE);
}

// list should have no blank spaces
export function collapseOperators(list, operations) {
  const result = [];
  let i = 0;

  while (i < list.length) {
    if (operations.includes(list[i])) {
      let j = i + 1;
      while (j < list.length && list[j] === list[i]) {
        j += 1;
      }

      result.push(list[i]);
      i = j;
    } else {
      result.push(list[i]);
      i += 1;
    }
  }

  return result;
}

// list should have no blank spaces
export function collapseListLeft(list, operations = OPERATORS) {
  const compacted = collapseOperators(list, operations);
  const result = [];
  let i = 0;

  while (i >= 0 && i < compacted.length) {
    if (
      i < compacted.length - 2 &&
      !operations.includes(compacted[i]) &&
      operations.includes(compacted[i + 1]) &&
      !operations.includes(compacted[i + 2])
    ) {
      result.push(evaluate(compacted[i], compacted[i + 1], compacted[i + 2]));
      i += 3;
    } else {
      result.push(compacted[i]);
      i += 1;
    }
  }

  return result;
}

export function collapseListRight(list, operations = OPERATORS) {
  const compacted = collapseOperators(list, operations);
  const result = [];
  let i = compacted.length - 1;

  while (i >= 0 && i < compacted.length) {
    if (
      i >= 2 &&
      !operations.includes(compacted[i]) &&
      operations.includes(compacted[i - 1]) &&
      !operations.includes(compacted[i - 2])
    ) {
      result.push(evaluate(compacted[i - 2], compacted[i - 1], compacted[i]));
      i -= 3;
    } else {
      result.push(compacted[i]);
      i -= 1;
    }
  }

  result.reverse();
  return result;
}

export function outOfBounds(grid, upperBound = 1000, lowerBound = -1000) {
  for (const row of grid) {
    for (const element of row) {
      if (element !== SPACE && !OPERATORS.includes(element)) {
        const value = Number.parseInt(String(element), 10);
        if (value < lowerBound || value > upperBound) {
          return true;
        }
      }
    }
  }
  return false;
}

function gridEquals(a, b) {
  if (a.length !== b.length) {
    return false;
  }
  for (let i = 0; i < a.length; i += 1) {
    if (a[i].length !== b[i].length) {
      return false;
    }
    for (let j = 0; j < a[i].length; j += 1) {
      if (a[i][j] !== b[i][j]) {
        return false;
      }
    }
  }
  return true;
}

export class Game {
  constructor(
    grid,
    numRows,
    numCols,
    generatedOperations,
    probOperations,
    generatedDigits,
    numGeneratedTiles,
    seed,
  ) {
    this._grid = grid;
    this._num_rows = numRows;
    this._num_cols = numCols;
    this._blank_spaces = this.#addBlankSpaces();
    this._generated_operations = generatedOperations;
    this._prob_operations = probOperations;
    this._generated_digits = generatedDigits;
    this._num_generated_tiles = numGeneratedTiles;
    this._seed = seed;
    this._rng = new DeterministicRNG(seed);
  }

  getNumRows() {
    return this._num_rows;
  }

  getNumCols() {
    return this._num_cols;
  }

  getGeneratedOperations() {
    return this._generated_operations;
  }

  getProbOperations() {
    return this._prob_operations;
  }

  getGeneratedDigits() {
    return this._generated_digits;
  }

  getNumGeneratedTilesPerTurn() {
    return this._num_generated_tiles;
  }

  getSeed() {
    return this._seed;
  }

  characterStr(character) {
    return String(character);
  }

  getBlankSpaces() {
    return this._blank_spaces;
  }

  #addBlankSpaces() {
    const blankSpaces = [];
    for (let i = 0; i < this._num_rows; i += 1) {
      for (let j = 0; j < this._num_cols; j += 1) {
        blankSpaces.push([i, j]);
      }
    }
    return blankSpaces;
  }

  updateBlankSpaces() {
    const blankSpaces = [];
    for (let i = 0; i < this._num_rows; i += 1) {
      for (let j = 0; j < this._num_cols; j += 1) {
        if (this._grid[i][j] === SPACE) {
          blankSpaces.push([i, j]);
        }
      }
    }
    this._blank_spaces = blankSpaces;
  }

  getGame() {
    return this._grid;
  }

  setGame(grid) {
    this._grid = grid;
  }

  generateTiles() {
    const numBlankSpaces = this._blank_spaces.length;
    const numTilesToGenerate = Math.min(numBlankSpaces, this._num_generated_tiles);
    const selectedIndices = this._rng.sample(
      Array.from({ length: numBlankSpaces }, (_, idx) => idx),
      numTilesToGenerate,
    );

    for (const currentIndex of selectedIndices) {
      const [row, col] = this._blank_spaces[currentIndex];

      if (this._rng.random() <= this._prob_operations) {
        this._grid[row][col] = this._rng.choice(this._generated_operations);
      } else {
        this._grid[row][col] = this._rng.choice(this._generated_digits);
      }
    }

    selectedIndices.sort((a, b) => b - a);
    for (const idx of selectedIndices) {
      this._blank_spaces.splice(idx, 1);
    }
  }

  left() {
    const newGrid = [];
    for (let i = 0; i < this._num_rows; i += 1) {
      const collapsedRow = collapseListLeft(removeExtraSpaces(this._grid[i]));
      const padding = Array.from({ length: this._num_cols - collapsedRow.length }, () => SPACE);
      newGrid.push([...collapsedRow, ...padding]);
    }
    return newGrid;
  }

  right() {
    const newGrid = [];
    for (let i = 0; i < this._num_rows; i += 1) {
      const collapsedRow = collapseListRight(removeExtraSpaces(this._grid[i]));
      const padding = Array.from({ length: this._num_cols - collapsedRow.length }, () => SPACE);
      newGrid.push([...padding, ...collapsedRow]);
    }
    return newGrid;
  }

  up() {
    const newGrid = constructGrid(this._num_rows, this._num_cols, SPACE);

    for (let j = 0; j < this._num_cols; j += 1) {
      const originalColumn = [];
      for (let i = 0; i < this._num_rows; i += 1) {
        originalColumn.push(this._grid[i][j]);
      }

      const collapsedCol = collapseListLeft(removeExtraSpaces(originalColumn));
      const padding = Array.from({ length: this._num_rows - collapsedCol.length }, () => SPACE);
      const currentCol = [...collapsedCol, ...padding];

      for (let i = 0; i < this._num_rows; i += 1) {
        newGrid[i][j] = currentCol[i];
      }
    }

    return newGrid;
  }

  down() {
    const newGrid = constructGrid(this._num_rows, this._num_cols, SPACE);

    for (let j = 0; j < this._num_cols; j += 1) {
      const originalColumn = [];
      for (let i = 0; i < this._num_rows; i += 1) {
        originalColumn.push(this._grid[i][j]);
      }

      const collapsedCol = collapseListRight(removeExtraSpaces(originalColumn));
      const padding = Array.from({ length: this._num_rows - collapsedCol.length }, () => SPACE);
      const currentCol = [...padding, ...collapsedCol];

      for (let i = 0; i < this._num_rows; i += 1) {
        newGrid[i][j] = currentCol[i];
      }
    }

    return newGrid;
  }

  getValidMoves() {
    const validMoves = [];
    if (!gridEquals(this.up(), this._grid)) {
      validMoves.push("up");
    }
    if (!gridEquals(this.down(), this._grid)) {
      validMoves.push("down");
    }
    if (!gridEquals(this.left(), this._grid)) {
      validMoves.push("left");
    }
    if (!gridEquals(this.right(), this._grid)) {
      validMoves.push("right");
    }
    return validMoves;
  }

  slideUp() {
    const newGrid = this.up();
    if (!gridEquals(newGrid, this._grid)) {
      this._grid = newGrid;
      this.updateBlankSpaces();
    }
  }

  slideDown() {
    const newGrid = this.down();
    if (!gridEquals(newGrid, this._grid)) {
      this._grid = newGrid;
      this.updateBlankSpaces();
    }
  }

  slideLeft() {
    const newGrid = this.left();
    if (!gridEquals(newGrid, this._grid)) {
      this._grid = newGrid;
      this.updateBlankSpaces();
    }
  }

  slideRight() {
    const newGrid = this.right();
    if (!gridEquals(newGrid, this._grid)) {
      this._grid = newGrid;
      this.updateBlankSpaces();
    }
  }

  isWon() {
    for (let i = 0; i < this._num_rows; i += 1) {
      for (let j = 0; j < this._num_cols; j += 1) {
        if (this._grid[i][j] === 67) {
          return true;
        }
      }
    }
    return false;
  }

  isLost(validMoves = null) {
    const moves = validMoves ?? this.getValidMoves();
    return !this.isWon() && (moves.length === 0 || outOfBounds(this._grid));
  }

  getState() {
    if (this.isWon()) {
      return "Won";
    }
    if (this.isLost()) {
      return "Lost";
    }
    return "In Progress";
  }
}
