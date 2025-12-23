"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const ROWS = 6;
const COLS = 7;
const TILE_SIZE = 70;
const OPERATORS = ["+", "-", "*"];

let idCounter = 0;

// Generate a random tile object
function randomTile() {
  const value = Math.random() < 0.5
    ? Math.floor(Math.random() * 10).toString()
    : OPERATORS[Math.floor(Math.random() * OPERATORS.length)];
  return { id: idCounter++, value };
}

// Initialize empty grid
function initGrid() {
  const g = Array.from({ length: ROWS }, () =>
    Array.from({ length: COLS }, () => ({ id: idCounter++, value: "_" }))
  );

  // Spawn 2 random tiles
  for (let i = 0; i < 2; i++) {
    const r = Math.floor(Math.random() * ROWS);
    const c = Math.floor(Math.random() * COLS);
    g[r][c] = randomTile();
  }

  return g;
}

// Collapse a single row left
function collapseRowLeft(row) {
  const newRow = row.filter((tile) => tile.value !== "_");

  for (let i = 0; i < newRow.length - 2; i++) {
    const a = newRow[i],
      op = newRow[i + 1],
      b = newRow[i + 2];

    if (!isNaN(a.value) && OPERATORS.includes(op.value) && !isNaN(b.value)) {
      const numA = parseInt(a.value, 10);
      const numB = parseInt(b.value, 10);
      let result = 0;

      if (op.value === "+") result = numA + numB;
      else if (op.value === "-") result = numA - numB;
      else if (op.value === "*") result = numA * numB;

      newRow.splice(i, 3, { id: a.id, value: result.toString() });
    }
  }

  while (newRow.length < row.length) newRow.push({ id: idCounter++, value: "_" });
  return newRow;
}

// Rotate grid clockwise
function rotateGrid(grid) {
  const newGrid = [];
  for (let c = 0; c < grid[0].length; c++) {
    const col = [];
    for (let r = grid.length - 1; r >= 0; r--) {
      col.push(grid[r][c]);
    }
    newGrid.push(col);
  }
  return newGrid;
}

export default function Grid() {
  const [grid, setGrid] = useState(null);

  // Only initialize grid on client
  useEffect(() => setGrid(initGrid()), []);

  const move = (direction) => {
    if (!grid) return;

    setGrid((prev) => {
      let newGrid = prev.map((row) => [...row]);

      // Rotate grid for uniform left collapse
      if (direction === "up") newGrid = rotateGrid(rotateGrid(rotateGrid(newGrid)));
      if (direction === "down") newGrid = rotateGrid(newGrid);
      if (direction === "right") newGrid.forEach((row) => row.reverse());

      // Collapse rows
      let collapsed = newGrid.map(collapseRowLeft);

      // Reverse rotation
      if (direction === "right") collapsed.forEach((row) => row.reverse());
      if (direction === "up") collapsed = rotateGrid(collapsed);
      if (direction === "down") collapsed = rotateGrid(rotateGrid(rotateGrid(collapsed)));

      // Spawn a new tile
      const emptyCells = [];
      collapsed.forEach((row, r) =>
        row.forEach((tile, c) => {
          if (tile.value === "_") emptyCells.push([r, c]);
        })
      );

      if (emptyCells.length > 0) {
        const [r, c] = emptyCells[Math.floor(Math.random() * emptyCells.length)];
        collapsed[r][c] = randomTile();
      }

      return collapsed;
    });
  };

  // Arrow key support
  useEffect(() => {
    const handleKey = (e) => {
      if (!grid) return;
      if (e.key === "ArrowUp") move("up");
      if (e.key === "ArrowDown") move("down");
      if (e.key === "ArrowLeft") move("left");
      if (e.key === "ArrowRight") move("right");
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [grid]);

  if (!grid) return null;

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>67! Game Mock</h1>

      <div
        style={{
          ...styles.grid,
          width: COLS * TILE_SIZE,
          height: ROWS * TILE_SIZE,
        }}
      >
        <AnimatePresence>
          {grid.map((row, r) =>
            row.map((tile, c) => (
              <motion.div
  key={`${r}-${c}-${tile.id}`} // now guaranteed unique
  layout
  initial={{ scale: 0.8, opacity: 0 }}
  animate={{ scale: 1, opacity: 1 }}
  exit={{ scale: 0.5, opacity: 0 }}
  transition={{ type: "spring", stiffness: 300, damping: 30 }}
  style={{
    ...styles.tile,
    backgroundColor: OPERATORS.includes(tile.value)
      ? "#0af"
      : tile.value === "_"
      ? "#ccc"
      : "#f0a",
    color: tile.value === "_" ? "#888" : "white",
  }}
>
  {tile.value === "_" ? "" : tile.value}
</motion.div>

            ))
          )}
        </AnimatePresence>
      </div>

      <div style={styles.controls}>
        <button onClick={() => move("up")} style={styles.button}>
          Up
        </button>
        <div style={{ marginTop: 8 }}>
          <button onClick={() => move("left")} style={styles.button}>
            Left
          </button>
          <button
            onClick={() => move("right")}
            style={{ ...styles.button, marginLeft: 8 }}
          >
            Right
          </button>
        </div>
        <button
          onClick={() => move("down")}
          style={{ ...styles.button, marginTop: 8 }}
        >
          Down
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: { padding: 20, textAlign: "center" },
  title: { fontSize: 32, marginBottom: 20 },
  grid: {
    display: "grid",
    gridTemplateRows: `repeat(${ROWS}, ${TILE_SIZE}px)`,
    gridTemplateColumns: `repeat(${COLS}, ${TILE_SIZE}px)`,
    gap: 6,
    justifyContent: "center",
    marginBottom: 20,
    position: "relative",
  },
  tile: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
    border: "1px solid #ccc",
    fontSize: 24,
    fontWeight: "bold",
    boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
    width: TILE_SIZE,
    height: TILE_SIZE,
  },
  controls: { marginTop: 20 },
  button: {
    padding: "10px 20px",
    fontSize: 18,
    borderRadius: 6,
    border: "none",
    backgroundColor: "#0070f3",
    color: "white",
    cursor: "pointer",
  },
};
