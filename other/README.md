# Project Program for 2025 CSC

## 67! (Inspired by 2048)
Start with an m by n grid and 2 randomly generated tiles. The goal of the game is to get the **67** tile.

Each generated tile is either an arithmetic operation (+ - *) (50% chance) or a digit (50% chance). The divide (/) operation is not included.
A number tile can be negative or have more than 1 digit, but each initial number tile will be between 0 to 9.

In this doc, empty spaces are denoted _. Currently, the modified version is used (game_modified.py).

---

## Demo

A 4 by 4 version (unmodified version):
[Watch on Youtube](https://youtu.be/Vp3NuS2XSRU)

---

## In each round
- 2 random tiles (not necessarily distinct) are generated in random positions
- The player can press up, down, left, or right, and the tiles will move around, similar to 2048
- Tiles can also collapse. If 3 consecutive tiles in the same row are of the form n1, +/-, n2, the tiles will collapse to a single number tile with value (n1 +/- n2) upon pressing left/right. The collapsing mechanics are similar for columns
- Different number tiles CANNOT be chained together. For example, upon pressing left, the row “1” “+” “2” “3” collapses to “3” “3” instead of “24”
- If no move can be made, the player loses
- If the 67 tile is made after a move, the player wins

---

## More about collapsing mechanics
Overall, the collapsing mechanics are somewhat similar to 2048.

These are more detailed collapsing mechanics
- In a series of chained operations, only 1 operation is simplified at a time
  - Upon pressing left, a "1 + 2 + 3" column simplifies to "_ _ 3 + 3" instead of "_ _ _ _ 6"
  - Upon pressing right, a "5 - 9 - 3" column simplifies to "_ _ 5 - 6" instead of "_ _ -4 - 3"
- Operations are always from left to right or from up to down
  - Upon pressing right, a "5 - 4" column collapses to "_ _ 1" instead of "_ _ -1"
- If there are gaps between a binary arithmetic expression, collapsing would get rid of the extra gaps **and** simplify the expression into a single number tile (for the modified version).
  - Upon pressing left, "8 + _ 0" simplifies to "8 _ _ _" instead of "8 + 0 _" for the unmodified version
- If there are no gaps between a binary arithmetic expression, collapsing would simplify it into a single number tile
  - Upon pressing left, "_ 1 + 2 _" simplifies to "3 _ _ _ _" instead of "1 + 2 _ _"

---

## Statistics
Below are the statistics of trial runs with randomly-generated moves:

**Only +, - included:**

| Grid Size | # Games | # Wins | Win% | Avg.# Moves (Overall) | Avg.# Moves (Win)
|-----------|---------|--------|------|-----------------------|------------------|
| 6 x 7 | 10,000 | 3 | 0.03 | ... | ... |
| 7 x 7 | 10,000 | 9 | 0.09 | ... | ... |
| 8 x 8 | 10,000 | 117 | 1.17 | 137 | 180 |
| 9 x 9 | 1,000 | 93 | 9.30 | 320 | 337 |
| 10 x 10 | 1,000 | 239 | 23.9 | 641 | 679 |

**+, -, \* included:**

| Grid Size | # Games | # Wins | Win% | Avg.# Moves (Overall) | Avg.# Moves (Win)
|-----------|---------|--------|------|-----------------------|------------------|
| 6 x 7 | 10,000 | 125 | 1.25 | 49 | 41 |
| 7 x 7 | 10,000 | 221 | 2.21 | 68 | 53 |
| 8 x 8 | 10,000 | 532 | 5.32 | 134 | 99 |
| 9 x 9 | 1,000 | 118 | 11.8 | 298 | 194 |
| 10 x 10 | 1,000 | 292 | 29.2 | 632 | 563 |

**+, -, \* included (modified version):**

| Grid Size | # Games | # Wins | Win% | Avg.# Moves (Overall) | Avg.# Moves (Win)
|-----------|---------|--------|------|-----------------------|------------------|
| 6 x 7 | 10,000 | 167 | 1.67 | 51 | 39 |
| 7 x 7 | 10,000 | 232 | 2.32 | 71 | 54 |
| 8 x 8 | 10,000 | 538 | 5.38 | 141 | 104 |
| 9 x 9 | 1,000 | 125 | 12.5 | 311 | 218 |
| 10 x 10 | 1,000 | 294 | 29.4 | 643 | 542 |

I also tried the 6 x 7 with the multiplication operation included (unmodified version).
I won 1 game out of 6, and the games took 57 moves on average.

---