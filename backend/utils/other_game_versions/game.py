import random

def construct_grid(num_rows: int, num_cols: int, item: str) -> list[list[str]]:
    grid = []
    for i in range (num_rows):
        cur_row = []
        for j in range (num_cols):
            cur_row.append(item)
        grid.append(cur_row)
    return grid

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

def collapse_list(lst: list[str], dir: str, operations: list[str] = ["+", "-", "*"]) -> list[str]:
    result = []
    padding = []

    if dir == "left":
        i = 0
        while i < len(lst):
            if lst[i] == "":
                i += 1
            elif (i < len(lst) - 2 and
                  lst[i] not in operations and lst[i] != "" and
                  lst[i + 1] in operations and
                  lst[i + 2] not in operations and lst[i + 2] != ""):
                result.append(evaluate(int(lst[i]), lst[i + 1], int(lst[i + 2])))
                i += 3
            else:
                result.append(lst[i])
                i += 1
    else:
        i = len(lst) - 1
        while i >= 0:
            if lst[i] == "":
                i -= 1
            elif (i >= 2 and
                  lst[i] not in operations and lst[i] != "" and
                  lst[i - 1] in operations and
                  lst[i - 2] not in operations and lst[i - 2] != ""):
                result.append(evaluate(int(lst[i - 2]), lst[i - 1], int(lst[i])))
                i -= 3
            else:
                result.append(lst[i])
                i -= 1
        result.reverse()

    for i in range(len(lst) - len(result)):
        padding.append("")

    if dir == "left":
        return result + padding
    else:
        return padding + result

class Game:

    def __add_blank_spaces(self) -> list[tuple[int, int]]:
        all_blanks = []
        for i in range (self._num_rows):
            for j in range (self._num_cols):
                all_blanks.append((i, j))
        return all_blanks

    def __update_blank_spaces(self) -> None:
        all_blanks = []
        for i in range(self._num_rows):
            for j in range(self._num_cols):
                if self._grid[i][j] == "":
                    all_blanks.append((i, j))
        self._blank_spaces = all_blanks

    def __init__(self, num_rows: int, num_cols: int):
        self._grid = construct_grid(num_rows, num_cols, "")
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._blank_spaces = self.__add_blank_spaces()
        self._generated_operations = ["+", "-", "*"]
        self._prob_operations = 0.5
        self._generated_digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self._num_generated_tiles = 2
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
        for i in range (self._num_rows):
            new_grid.append(collapse_list(self._grid[i], "left"))
        return new_grid

    def right(self) -> list[list[str]]:
        new_grid = []
        for i in range (self._num_rows):
            cur_row = collapse_list(self._grid[i], "right")
            new_grid.append(cur_row)
        return new_grid

    def up(self) -> list[list[str]]:
        new_grid = construct_grid(self._num_rows, self._num_cols, " ")

        for j in range (self._num_cols):
            orig_col = []
            for i in range (self._num_rows):
                orig_col.append(self._grid[i][j])

            cur_col = collapse_list(orig_col, "left")
            for i in range (self._num_rows):
                new_grid[i][j] = cur_col[i]

        return new_grid

    def down(self) -> list[list[str]]:
        new_grid = construct_grid(self._num_rows, self._num_cols, " ")

        for j in range(self._num_cols):
            orig_col = []
            for i in range(self._num_rows):
                orig_col.append(self._grid[i][j])

            cur_col = collapse_list(orig_col, "right")
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
                if self._grid[i][j] == 67:
                    return True
        return False

    def is_lost(self) -> bool:
        return not self.is_won() and len(self.get_valid_moves()) == 0

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

def auto_play(num_rows: int, num_cols: int) -> list[int]:
    game = Game(num_rows, num_cols)
    round_num = 1

    while True:
        game.generate_tiles()
        valid_moves = game.get_valid_moves()

        if len(valid_moves) == 0:
            return [0, round_num]

        move = random.choice(valid_moves)
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
        else:
            round_num += 1

def bot_trials(num_rows: int, num_cols: int, num_trials: int) -> None:
    wins = 0
    losses = 0
    total_moves = 0
    win_moves = 0
    for i in range(num_trials):
        cur_result = auto_play(num_rows, num_cols)
        if cur_result[0] == 1:
            wins += 1
            win_moves += cur_result[1]
        else:
            losses += 1
        total_moves += cur_result[1]
    print(f"Wins: {wins}, Losses: {losses}, Average number of moves: {total_moves / num_trials}, Total win moves: {win_moves}")

if __name__ == "__main__":
    bot_trials(6, 7, 10000)
    #human_play(6, 7)
