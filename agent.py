"""AI agents for Tic-Tac-Toe: Random, Heuristic, and Minimax (with Alpha-Beta)."""

import math
import random
import time

from game import TicTacToe, PLAYER_X, PLAYER_O, EMPTY, WINNING_LINES, opponent

CENTER = 4
CORNERS = (0, 2, 6, 8)
EDGES = (1, 3, 5, 7)


def find_winning_move(game, player):
    """Return a position that completes a line for player right now, or None."""
    for a, b, c in WINNING_LINES:
        cells = [game.board[a], game.board[b], game.board[c]]
        if cells.count(player) == 2 and cells.count(EMPTY) == 1:
            return (a, b, c)[cells.index(EMPTY)]
    return None


class RandomAgent:
    """Easy: picks uniformly at random among the legal moves."""

    name = "Random"

    def __init__(self, player=PLAYER_X, seed=None):
        self.player = player
        self.rng = random.Random(seed)

    def get_move(self, game):
        moves = game.get_available_moves()
        return self.rng.choice(moves) if moves else None


class HeuristicAgent:
    """Medium: Immediate Win > Immediate Block > Center > Corners > Edges."""

    name = "Heuristic"

    def __init__(self, player=PLAYER_X, seed=None):
        self.player = player
        self.rng = random.Random(seed)
        self.last_rule = None

    def get_move(self, game):
        moves = game.get_available_moves()
        if not moves:
            return None

        win = find_winning_move(game, self.player)
        if win is not None:
            self.last_rule = "win"
            return win

        block = find_winning_move(game, opponent(self.player))
        if block is not None:
            self.last_rule = "block"
            return block

        if CENTER in moves:
            self.last_rule = "center"
            return CENTER

        for rule, group in (("corner", CORNERS), ("edge", EDGES)):
            options = [m for m in group if m in moves]
            if options:
                self.last_rule = rule
                return self.rng.choice(options)
        return None


class MinimaxAgent:
    """Hard: full-depth Minimax search, optionally with Alpha-Beta pruning.

    Terminal scores are depth-adjusted so the agent prefers fast wins and
    delays losses: a win scores +10 - depth, a loss depth - 10, a draw 0.
    """

    name = "Minimax"

    def __init__(self, player=PLAYER_O, use_alpha_beta=True):
        self.player = player
        self.use_alpha_beta = use_alpha_beta
        self.nodes_visited = 0
        self.move_scores = {}
        self.search_time_ms = 0.0

    def get_move(self, game):
        moves = game.get_available_moves()
        if not moves or game.is_game_over():
            return None

        # Search a copy so the caller's game is never touched.
        state = game.copy()
        self.nodes_visited = 0
        self.move_scores = {}
        start = time.perf_counter()

        best_move, best_score = None, -math.inf
        for move in moves:
            state.make_move(move, self.player)
            # Each root child gets a full window so the reported candidate
            # scores are exact; pruning still happens inside each subtree.
            score = self._minimax(state, 1, False, -math.inf, math.inf)
            state.undo_move(move)
            self.move_scores[move] = score
            if score > best_score:
                best_move, best_score = move, score

        self.search_time_ms = (time.perf_counter() - start) * 1000
        return best_move

    def _minimax(self, state, depth, maximizing, alpha, beta):
        self.nodes_visited += 1

        winner = state.check_winner()
        if winner == self.player:
            return 10 - depth
        if winner is not None:
            return depth - 10
        if state.is_full():
            return 0

        mover = self.player if maximizing else opponent(self.player)
        best = -math.inf if maximizing else math.inf
        for move in state.get_available_moves():
            state.make_move(move, mover)
            score = self._minimax(state, depth + 1, not maximizing, alpha, beta)
            state.undo_move(move)

            if maximizing:
                best = max(best, score)
                alpha = max(alpha, best)
            else:
                best = min(best, score)
                beta = min(beta, best)
            if self.use_alpha_beta and alpha >= beta:
                break  # the opponent will never allow this branch
        return best

    def get_stats(self):
        return {
            "nodes_visited": self.nodes_visited,
            "move_scores": dict(self.move_scores),
            "search_time_ms": round(self.search_time_ms, 3),
            "alpha_beta": self.use_alpha_beta,
        }


AGENTS = {
    "easy": RandomAgent,
    "random": RandomAgent,
    "medium": HeuristicAgent,
    "heuristic": HeuristicAgent,
    "hard": MinimaxAgent,
    "unbeatable": MinimaxAgent,
    "minimax": MinimaxAgent,
}


def create_agent(kind, player):
    """Build an agent from a difficulty or algorithm name (e.g. 'medium', 'minimax')."""
    try:
        return AGENTS[kind.lower()](player=player)
    except KeyError:
        raise ValueError(f"Unknown agent type: {kind!r}") from None


def play_game(agent1, agent2):
    """Play one game to completion. Returns the winning symbol, or None for a draw."""
    game = TicTacToe()
    agents = {agent1.player: agent1, agent2.player: agent2}
    while not game.is_game_over():
        agent = agents[game.current_player]
        game.make_move(agent.get_move(game), agent.player)
    return game.check_winner()


def simulate_match(agent1, agent2, num_games=100):
    """Play num_games between two agents (X always moves first) and tally results."""
    if agent1.player == agent2.player:
        raise ValueError("Agents must play different symbols")

    results = {"agent1_wins": 0, "agent2_wins": 0, "draws": 0}
    for _ in range(num_games):
        winner = play_game(agent1, agent2)
        if winner == agent1.player:
            results["agent1_wins"] += 1
        elif winner == agent2.player:
            results["agent2_wins"] += 1
        else:
            results["draws"] += 1

    results["num_games"] = num_games
    for key in ("agent1_wins", "agent2_wins", "draws"):
        rate_key = key.replace("_wins", "_win_rate").replace("draws", "draw_rate")
        results[rate_key] = round(results[key] / num_games, 4) if num_games else 0.0
    return results
