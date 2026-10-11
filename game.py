"""Tic-Tac-Toe game engine: board representation, moves, and rules."""

PLAYER_X = 'X'
PLAYER_O = 'O'
EMPTY = ' '

# Board positions are indexed 0-8, row by row:
#   0 | 1 | 2
#   3 | 4 | 5
#   6 | 7 | 8
WINNING_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)


def opponent(player):
    """Return the other player's symbol."""
    return PLAYER_O if player == PLAYER_X else PLAYER_X


class TicTacToe:
    def __init__(self, board=None, current_player=None):
        if board is None:
            self.board = [EMPTY] * 9
        else:
            if len(board) != 9:
                raise ValueError("Board must have exactly 9 cells")
            self.board = list(board)

        if current_player is None:
            # X always moves first, so X is to move whenever counts are equal.
            x_count = self.board.count(PLAYER_X)
            o_count = self.board.count(PLAYER_O)
            current_player = PLAYER_X if x_count <= o_count else PLAYER_O
        self.current_player = current_player

    def reset(self):
        self.board = [EMPTY] * 9
        self.current_player = PLAYER_X

    def copy(self):
        return TicTacToe(board=self.board, current_player=self.current_player)

    def get_available_moves(self):
        return [i for i, cell in enumerate(self.board) if cell == EMPTY]

    def is_valid_move(self, pos):
        return (
            isinstance(pos, int)
            and 0 <= pos < 9
            and self.board[pos] == EMPTY
            and not self.is_game_over()
        )

    def make_move(self, pos, player=None):
        """Place a mark at pos. Returns True on success, False if illegal.

        If player is omitted, the current player moves. After a successful
        move, the turn passes to the opponent of whoever just moved.
        """
        if not self.is_valid_move(pos):
            return False
        if player is None:
            player = self.current_player
        self.board[pos] = player
        self.current_player = opponent(player)
        return True

    def undo_move(self, pos):
        """Clear pos and hand the turn back to the player who made that move."""
        player = self.board[pos]
        if player == EMPTY:
            return False
        self.board[pos] = EMPTY
        self.current_player = player
        return True

    def get_winning_line(self):
        """Return the (a, b, c) indices of the winning line, or None."""
        for line in WINNING_LINES:
            a, b, c = line
            if self.board[a] != EMPTY and self.board[a] == self.board[b] == self.board[c]:
                return line
        return None

    def check_winner(self):
        """Return PLAYER_X or PLAYER_O if someone has won, otherwise None."""
        line = self.get_winning_line()
        return self.board[line[0]] if line else None

    def is_full(self):
        return EMPTY not in self.board

    def is_draw(self):
        return self.is_full() and self.check_winner() is None

    def is_game_over(self):
        return self.check_winner() is not None or self.is_full()

    def to_dict(self):
        """JSON-friendly snapshot of the game state (used by the Flask API)."""
        return {
            "board": list(self.board),
            "current_player": self.current_player,
            "winner": self.check_winner(),
            "winning_line": self.get_winning_line(),
            "is_draw": self.is_draw(),
            "is_game_over": self.is_game_over(),
            "available_moves": self.get_available_moves(),
        }

    def __str__(self):
        rows = []
        for r in range(3):
            rows.append(" | ".join(self.board[r * 3:r * 3 + 3]))
        return "\n---------\n".join(rows)
