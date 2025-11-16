import gymnasium as gym
from gymnasium import spaces
import numpy as np

from game import Game

import sys # temp debug

LOWER_BOUND = -1000
UPPER_BOUND = 1000

class SixSevenEnv(gym.Env):
    """
    Gymnasium environment wrapper for the 67 game.

    The agent receives the game grid as observation and selects moves (up, down, left, right).
    Rewards are given for:
    - Winning the game (reaching 67)
    - Each valid move that changes the board state
    - Penalty for invalid moves
    """

    def __init__(self, num_rows: int = 6, num_cols: int = 7):
        """
        Initialize the environment.

        Args:
            num_rows: Number of rows in the game grid
            num_cols: Number of columns in the game grid
        """
        super().__init__()

        self.num_rows = num_rows
        self.num_cols = num_cols
        self.game = Game(num_rows, num_cols)

        # Action space: 0=up, 1=down, 2=left, 3=right
        self.action_space = spaces.Discrete(4)

        # Observation space: Grid represented as a flattened array of encoded values
        # We'll encode: empty="", digits 0-9, operators +/-/* as unique integer values
        # Empty: 0, Digits 0-9: 1-10, Operators +: 11, -: 12, *: 13
        self.observation_space = spaces.Box(
            low=LOWER_BOUND, high=UPPER_BOUND, shape=(num_rows * num_cols * 2,), dtype=np.int32
        )

        self.action_map = {0: "up", 1: "down", 2: "left", 3: "right"}
        self.steps = 0
        self.max_steps = 500  # Maximum steps per episode

    def _encode_cell(self, cell_value):
        """Stores 2 values: digit/[operator or empty]
           What if cell_value = 0"""
        try: 
            return [cell_value, 0, 0, 0, 0] # don't understand how still exceeds 500
        except ValueError:
            cell_value = str(cell_value)
            if cell_value == "": # change this
                return [0, 1, 0, 0, 0]
            elif cell_value == "+":
                return [0, 0, 1, 0, 0]
            elif cell_value == "-":
                return [0, 0, 0, 1, 0]
            elif cell_value == "*":
                return [0, 0, 0, 0, 1]

    def _get_observation(self, grid: list[list[str]] = None):
        """Convert game grid to observation array."""
        if grid is None:    # allows for conversion of arbitrary grid
            grid = self.game._grid

        obs = np.zeros(self.num_rows * self.num_cols * 5, dtype=np.int32)
        flat_idx = 0
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                obs[flat_idx:flat_idx + 5] = self._encode_cell(grid[i][j])
                flat_idx += 5

        return obs

    def _get_info(self):
        """Get info dictionary."""
        return {
            "valid_moves": self.game.get_valid_moves(),
            "steps": self.steps,
        }

    def reset(self, seed=None, options=None):
        """
        Reset the environment to initial state.
        Returns:
            observation: Initial observation
            info: Info dictionary
        """
        super().reset(seed=seed)

        self.game = Game(self.num_rows, self.num_cols)
        self.game.generate_tiles()
        self.steps = 0

        observation = self._get_observation()
        info = self._get_info()

        return observation, info

    def step(self, action):
        """
        Execute one step of the environment.

        Args:
            action: Action to take (0=up, 1=down, 2=left, 3=right)

        Returns:
            observation: New observation
            reward: Reward for this step
            terminated: Whether the episode ended (win/loss)
            truncated: Whether the episode was truncated (max steps)
            info: Info dictionary
        """
        self.steps += 1

        valid_moves = self.game.get_valid_moves()
        move_name = self.action_map[action]

        reward = 0.0

        if move_name not in valid_moves:
            reward = -0.1 # invalid move penalty
        else:
            reward = -0.01

            # Execute the move
            if move_name == "up":
                self.game.slide_up()
            elif move_name == "down":
                self.game.slide_down()
            elif move_name == "left":
                self.game.slide_left()
            else:  # right
                self.game.slide_right()

            # Generate new tiles after move
            self.game.generate_tiles()

        # Get new observation
        observation = self._get_observation()
        info = self._get_info()

        # Check terminal conditions
        terminated = False
        truncated = False

        if self.game.is_won():
            reward += 10.0  # Win bonus
            terminated = True
        elif self.game.is_lost():
            reward += -1.0  # Loss penalty
            terminated = True

        if self.steps >= self.max_steps:
            truncated = True

        return observation, reward, terminated, truncated, info

    def render(self):
        """Render the current game state."""
        print(self.game)

    def close(self):
        """Clean up resources."""
        pass


if __name__ == "__main__":
    # Test the environment
    env = SixSevenEnv()
    obs, info = env.reset()
    print("Initial observation shape:", obs.shape)
    print("Initial observation:", obs)
    print("Valid moves:", info["valid_moves"])

    # Run a few random steps
    for _ in range(10000):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Action: {env.action_map[action]}, Reward: {reward}, Valid moves: {info['valid_moves']}")
        print(env.render())

        if terminated or truncated:
            print("Episode ended")
            break
