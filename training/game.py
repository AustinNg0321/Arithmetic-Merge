import random

def construct_grid(num_rows: int, num_cols: int, item: str) -> list[list[str]]:
    return [[item for j in range(num_cols)] for i in range(num_rows)]

def evaluate(num_1: int, operator: str, num_2: int) -> int:
    match (operator):
        case "+":
            return num_1 + num_2
        case "-":
            return num_1 - num_2
        case "*":
            return num_1 * num_2
        case _:
            return 0

def remove_extra_spaces(lst: list[str]) -> list[str]:
    return [lst[i] for i in range(len(lst)) if lst[i] != ""]

# lst should have no blank spaces
def collapse_operators(lst: list[str], operations: list[str]) -> list[str]:
    result = []
    i = 0

    while i < len(lst):
        if lst[i] in operations:
            j = i + 1
            while j < len(lst) and lst[j] == lst[i]:
                j += 1

            result.append(lst[i])
            i = j
        else:
            result.append(lst[i])
            i += 1

    return result

# lst should have no blank spaces
def collapse_list_left(lst: list[str], operations: list[str] = ["+", "-", "*"]) -> list[str]:
    lst = collapse_operators(lst, operations)
    result = []
    i = 0

    while 0 <= i < len(lst):
        if (i < len(lst) - 2 and
            lst[i] not in operations and
            lst[i + 1] in operations and
            lst[i + 2] not in operations):
            result.append(str(evaluate(int(lst[i]), lst[i + 1], int(lst[i + 2]))))
            i += 3
        else:
            result.append(lst[i])
            i += 1

    return result

def collapse_list_right(lst: list[str], operations: list[str] = ["+", "-", "*"]) -> list[str]:
    lst = collapse_operators(lst, operations)
    result = []
    i = len(lst) - 1

    while 0 <= i < len(lst):
        if (i >= 2 and
            lst[i] not in operations and
            lst[i - 1] in operations and
            lst[i - 2] not in operations):
            result.append(str(evaluate(int(lst[i - 2]), lst[i - 1], int(lst[i]))))
            i -= 3
        else:
            result.append(lst[i])
            i -= 1

    result.reverse()
    return result

def out_of_bounds(grid: list[list[str]], upper_bound: int = 500, lower_bound: int = -500) -> bool:
    return any([any([int(el) < lower_bound or int(el) > upper_bound
                     for el in row if (el != "" and el not in "+-*")]) for row in grid])

class Game:

    def __add_blank_spaces(self) -> list[tuple[int, int]]:
        return [(i, j) for i in range(self._num_rows) for j in range(self._num_cols)]

    def __update_blank_spaces(self) -> None:
        self._blank_spaces = [(i, j) for i in range(self._num_rows) for j in range(self._num_cols)
                              if self._grid[i][j] == ""]

    def __init__(self, num_rows: int, num_cols: int):
        self._grid = construct_grid(num_rows, num_cols, "")
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._blank_spaces = self.__add_blank_spaces()
        self._generated_operations = ["+", "-", "*"]
        self._prob_operations = 0.67
        self._generated_digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self._num_generated_tiles = 4 # set this to somewhere between 2 to 4
        self._round_num = 1

    def __str__(self):
        board = ""
        for i in range (self._num_rows):
            cur_row = ""
            for j in range (self._num_cols):
                cur_row += f"| {self._grid[i][j]:^3} "
            cur_row += "|\n"
            board += cur_row
        return board

    def set_game(self, grid) -> None:
        self._grid = grid

    def generate_tiles(self) -> None:
        num_blank_spaces = len(self._blank_spaces)
        num_tiles_to_generate = min(num_blank_spaces, self._num_generated_tiles)

        for i in range (num_tiles_to_generate):
            cur_index = random.randint(0, num_blank_spaces - 1)
            cur_pos = self._blank_spaces[cur_index]

            if random.random() <= self._prob_operations:
                self._grid[cur_pos[0]][cur_pos[1]] = random.choice(self._generated_operations)
            else:
                self._grid[cur_pos[0]][cur_pos[1]] = random.choice(self._generated_digits)

            num_blank_spaces -= 1
            self._blank_spaces.pop(cur_index)

    def left(self) -> list[list[str]]:
        new_grid = []
        for i in range(self._num_rows):
            collapsed_row = collapse_list_left(remove_extra_spaces(self._grid[i]))
            padding = ["" for j in range(self._num_cols - len(collapsed_row))]
            new_grid.append(collapsed_row + padding)
        return new_grid

    def right(self) -> list[list[str]]:
        new_grid = []
        for i in range(self._num_rows):
            collapsed_row = collapse_list_right(remove_extra_spaces(self._grid[i]))
            padding = ["" for j in range(self._num_cols - len(collapsed_row))]
            new_grid.append(padding + collapsed_row)
        return new_grid

    def up(self) -> list[list[str]]:
        new_grid = construct_grid(self._num_rows, self._num_cols, "")

        for j in range(self._num_cols):
            orig_col = [self._grid[i][j] for i in range(self._num_rows)]
            collapsed_col = collapse_list_left(remove_extra_spaces(orig_col))
            padding = ["" for i in range(self._num_rows - len(collapsed_col))]
            cur_col = collapsed_col + padding
            for i in range(self._num_rows):
                new_grid[i][j] = cur_col[i]

        return new_grid

    def down(self) -> list[list[str]]:
        new_grid = construct_grid(self._num_rows, self._num_cols, "")

        for j in range(self._num_cols):
            orig_col = [self._grid[i][j] for i in range(self._num_rows)]
            collapsed_col = collapse_list_right(remove_extra_spaces(orig_col))
            padding = ["" for i in range(self._num_rows - len(collapsed_col))]
            cur_col = padding + collapsed_col
            for i in range(self._num_rows):
                new_grid[i][j] = cur_col[i]

        return new_grid

    def get_valid_moves(self) -> list[str]:
        valid_moves = []
        if self.up() != self._grid:
            valid_moves.append("up")
        if self.down() != self._grid:
            valid_moves.append("down")
        if self.left() != self._grid:
            valid_moves.append("left")
        if self.right() != self._grid:
            valid_moves.append("right")
        return valid_moves

    def slide_up(self) -> None:
        new_grid = self.up()
        if new_grid != self._grid:
            self._grid = new_grid
            self.__update_blank_spaces()

    def slide_down(self) -> None:
        new_grid = self.down()
        if new_grid != self._grid:
            self._grid = new_grid
            self.__update_blank_spaces()

    def slide_left(self) -> None:
        new_grid = self.left()
        if new_grid != self._grid:
            self._grid = new_grid
            self.__update_blank_spaces()

    def slide_right(self) -> None:
        new_grid = self.right()
        if new_grid != self._grid:
            self._grid = new_grid
            self.__update_blank_spaces()

    def is_won(self) -> bool:
        for i in range (self._num_rows):
            for j in range (self._num_cols):
                if self._grid[i][j] == "67":
                    return True
        return False

    def is_lost(self) -> bool:
        return not self.is_won() and (len(self.get_valid_moves()) == 0 or out_of_bounds(self._grid))

def human_play(num_rows: int, num_cols: int) -> bool:
    game = Game(num_rows, num_cols)
    round_num = 1

    while True:
        game.generate_tiles()
        valid_moves = game.get_valid_moves()
        print(game)

        if len(valid_moves) == 0:
            print(f"Game over after {round_num} rounds.")
            return False

        finished_move = False
        while not finished_move:
            move = input("Enter a move (up/down/left/right): ").lower()
            if move in valid_moves:
                if move == "up":
                    game.slide_up()
                elif move == "down":
                    game.slide_down()
                elif move == "left":
                    game.slide_left()
                else:
                    game.slide_right()
                print(game)
                finished_move = True
            else:
                print(f"{move} is not a legal move!")

        if game.is_won():
            print(f"Congratulations! You win after {round_num} moves.")
            return True
        else:
            round_num += 1

def random_bot(grid: list[list[str]], valid_moves: list[str]) -> None:
    return random.choice(valid_moves)

def auto_play(num_rows: int, num_cols: int, max_turns_per_game : int = 1000, model: callable = random_bot) -> list[int]:
    game = Game(num_rows, num_cols)
    round_num = 1

    while max_turns_per_game >= round_num:
        game.generate_tiles()
        valid_moves = game.get_valid_moves()

        if len(valid_moves) == 0:
            return [0, round_num] # *** overlap with loss condition ***

        move = model(game._grid, valid_moves)
        if move == "up" or move == "u":
            game.slide_up()
        elif move == "down" or move == "d":
            game.slide_down()
        elif move == "left" or move == "l":
            game.slide_left()
        else:
            game.slide_right()

        if game.is_won():
            return [1, round_num]
        elif game.is_lost():
            break
        else:
            round_num += 1

    return [0, round_num]

def bot_trials(num_rows: int, num_cols: int, num_trials: int, model: callable = random_bot) -> None:
    # metrics: 
    wins = 0
    losses = 0
    total_moves = 0
    win_moves = 0

    # run trials
    for i in range(num_trials):
        cur_result = auto_play(num_rows, num_cols, model=model)
        if cur_result[0] == 1:
            wins += 1
            win_moves += cur_result[1]
        else:
            losses += 1

        total_moves += cur_result[1]

    print(f"Wins: {wins}, Losses: {losses}, Average number of moves: {total_moves / num_trials}, Total win moves: {win_moves}")

if __name__ == "__main__":
    bot_trials(6, 7, 1000)
    #human_play(6, 7)
