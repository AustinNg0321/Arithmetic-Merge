import gymnasium as gym
from gymnasium import spaces
import numpy as np
from game_final import Game

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
            low=0, high=13, shape=(num_rows * num_cols,), dtype=np.int32
        )

        self.action_map = {0: "up", 1: "down", 2: "left", 3: "right"}
        self.steps = 0
        self.max_steps = 500  # Maximum steps per episode

    def _encode_cell(self, cell_value):
        """Convert cell value to integer encoding."""
        if cell_value == "":
            return 0
        elif cell_value in "0123456789":
            return int(cell_value) + 1  # 1-10
        elif cell_value == "+":
            return 11
        elif cell_value == "-":
            return 12
        elif cell_value == "*":
            return 13
        else:
            return 0  # Default for unknown values

    def _get_observation(self):
        """Convert game grid to observation array."""
        obs = np.zeros(self.num_rows * self.num_cols, dtype=np.int32)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                flat_idx = i * self.num_cols + j
                obs[flat_idx] = self._encode_cell(self.game._grid[i][j])
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
            reward = 0.01

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
    for _ in range(100):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Action: {env.action_map[action]}, Reward: {reward}, Valid moves: {info['valid_moves']}")
        print(env.render())

        if terminated or truncated:
            print("Episode ended")
            break
