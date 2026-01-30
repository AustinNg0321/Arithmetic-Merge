import random

ARITH_SEQ_NOT_FOUND = [-1, -1, -1]

# not found if the method returns something less than 0
def find_prev_nonempty_index(lst: list[str], end_index: int) -> int:
    while 0 <= end_index < len(lst) and lst[end_index] == "":
        end_index -= 1
    return end_index

# not found if the method returns something greater than or equal to len(lst)
def find_next_nonempty_index(lst: list[str], start_index: int) -> int:
    while 0 <= start_index < len(lst) and lst[start_index] == "":
        start_index += 1
    return start_index

# finds corresponding indices to the previous sequence with the format "num gap op gap num"
def find_prev_arith_seq(lst: list[str], end_index: int, operations: list[str]) -> list[int]:
    third_nonempty_index = find_prev_nonempty_index(lst, end_index)
    if third_nonempty_index < 0 or lst[third_nonempty_index] in operations:
        return ARITH_SEQ_NOT_FOUND

    second_nonempty_index = find_prev_nonempty_index(lst, third_nonempty_index - 1)
    if second_nonempty_index < 0 or lst[second_nonempty_index] not in operations:
        return ARITH_SEQ_NOT_FOUND

    first_nonempty_index = find_prev_nonempty_index(lst, second_nonempty_index - 1)
    if first_nonempty_index < 0 or lst[first_nonempty_index] in operations:
        return ARITH_SEQ_NOT_FOUND
    else:
        return [first_nonempty_index, second_nonempty_index, third_nonempty_index]

# finds corresponding indices to the next sequence with the format "num gap op gap num"
def find_next_arith_seq(lst: list[str], start_index: int, operations: list[str]) -> list[int]:
    first_nonempty_index = find_next_nonempty_index(lst, start_index)
    if first_nonempty_index >= len(lst) or lst[first_nonempty_index] in operations:
        return ARITH_SEQ_NOT_FOUND

    second_nonempty_index = find_next_nonempty_index(lst, first_nonempty_index + 1)
    if second_nonempty_index >= len(lst) or lst[second_nonempty_index] not in operations:
        return ARITH_SEQ_NOT_FOUND

    third_nonempty_index = find_next_nonempty_index(lst, second_nonempty_index + 1)
    if third_nonempty_index >= len(lst) or lst[third_nonempty_index] in operations:
        return ARITH_SEQ_NOT_FOUND
    else:
        return [first_nonempty_index, second_nonempty_index, third_nonempty_index]

def construct_grid(num_rows: int, num_cols: int, item: str) -> list[list[str]]:
    grid = []
    for i in range(num_rows):
        cur_row = []
        for j in range(num_cols):
            cur_row.append(item)
        grid.append(cur_row)
    return grid

def evaluate(num_1: int, operator: str, num_2: int) -> int:
    match operator:
        case "+":
            return num_1 + num_2
        case "-":
            return num_1 - num_2
        case "*":
            return num_1 * num_2
        case _:
            return 0

# Add padding in separate method in Game
def collapse_list_left(lst: list[str], operations: list[str] = ["+", "-", "*"]) -> list[str]:
    result = []
    i = 0
    while i < len(lst):
        next_arith_seq = find_next_arith_seq(lst, i, operations)
        if next_arith_seq != ARITH_SEQ_NOT_FOUND:
            result.append(evaluate(int(lst[next_arith_seq[0]]), lst[next_arith_seq[1]], int(lst[next_arith_seq[2]])))
            i = next_arith_seq[2] + 1
        else:
            next_nonempty_index = find_next_nonempty_index(lst, i)
            if next_nonempty_index >= len(lst):
                return result
            else:
                result.append(lst[next_nonempty_index])
                i = next_nonempty_index + 1
    return result

def collapse_list_right(lst: list[str], operations: list[str] = ["+", "-", "*"]) -> list[str]:
    result = []
    i = len(lst) - 1
    while i >= 0:
        prev_arith_seq = find_prev_arith_seq(lst, i, operations) # !!!
        if prev_arith_seq != ARITH_SEQ_NOT_FOUND:
            result.append(
                evaluate(int(lst[prev_arith_seq[0]]), lst[prev_arith_seq[1]], int(lst[prev_arith_seq[2]]))) # !!!
            i = prev_arith_seq[0] - 1
        else:
            prev_nonempty_index = find_prev_nonempty_index(lst, i)
            if prev_nonempty_index < 0:
                result.reverse()
                return result
            else:
                result.append(lst[prev_nonempty_index])
                i = prev_nonempty_index - 1
    result.reverse()
    return result

class Game:

    def __add_blank_spaces(self) -> list[tuple[int, int]]:
        all_blanks = []
        for i in range(self._num_rows):
            for j in range(self._num_cols):
                all_blanks.append((i, j))
        return all_blanks

    def update_blank_spaces(self) -> None:
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
        for i in range(self._num_rows):
            cur_row = ""
            for j in range(self._num_cols):
                cur_row += f"| {self._grid[i][j]:^3} "
            cur_row += "|\n"
            board += cur_row
        return board

    def generate_tiles(self) -> None:
        num_blank_spaces = len(self._blank_spaces)
        num_tiles_to_generate = min(num_blank_spaces, self._num_generated_tiles)

        for i in range(num_tiles_to_generate):
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
            collapsed_row = collapse_list_left(self._grid[i])
            padding = ["" for j in range(self._num_cols - len(collapsed_row))]
            new_grid.append(collapsed_row + padding)
        return new_grid

    def right(self) -> list[list[str]]:
        new_grid = []
        for i in range(self._num_rows):
            collapsed_row = collapse_list_right(self._grid[i])
            padding = ["" for j in range(self._num_cols - len(collapsed_row))]
            new_grid.append(padding + collapsed_row)
        return new_grid

    def up(self) -> list[list[str]]:
        new_grid = construct_grid(self._num_rows, self._num_cols, "")

        for j in range(self._num_cols):
            orig_col = [self._grid[i][j] for i in range(self._num_rows)]

            collapsed_col = collapse_list_left(orig_col)
            padding = ["" for i in range(self._num_rows - len(collapsed_col))]
            cur_col = collapsed_col + padding
            for i in range(self._num_rows):
                new_grid[i][j] = cur_col[i]

        return new_grid

    def down(self) -> list[list[str]]:
        new_grid = construct_grid(self._num_rows, self._num_cols, "")

        for j in range(self._num_cols):
            orig_col = [self._grid[i][j] for i in range(self._num_rows)]
            collapsed_col = collapse_list_right(orig_col)
            padding = ["" for i in range(self._num_rows - len(collapsed_col))]
            cur_col = padding + collapsed_col
            for i in range(self._num_rows):
                new_grid[i][j] = cur_col[i]

        return new_grid

    def get_valid_moves(self) -> list[str]:
        valid_moves = []
        up_grid = self.up()
        down_grid = self.down()
        left_grid = self.left()
        right_grid = self.right()
        if up_grid != self._grid:
            valid_moves.append("up")
        if down_grid != self._grid:
            valid_moves.append("down")
        if left_grid != self._grid:
            valid_moves.append("left")
        if right_grid != self._grid:
            valid_moves.append("right")
        return valid_moves

    def slide_up(self) -> None:
        new_grid = self.up()
        if new_grid != self._grid:
            self._grid = new_grid
            self.update_blank_spaces()

    def slide_down(self) -> None:
        new_grid = self.down()
        if new_grid != self._grid:
            self._grid = new_grid
            self.update_blank_spaces()

    def slide_left(self) -> None:
        new_grid = self.left()
        if new_grid != self._grid:
            self._grid = new_grid
            self.update_blank_spaces()

    def slide_right(self) -> None:
        new_grid = self.right()
        if new_grid != self._grid:
            self._grid = new_grid
            self.update_blank_spaces()

    def is_won(self) -> bool:
        for i in range(self._num_rows):
            for j in range(self._num_cols):
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
