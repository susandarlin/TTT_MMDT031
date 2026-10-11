"""Flask backend for the Tic-Tac-Toe AI visualizer.

The API is stateless: the browser sends the board with every request, and the
server rebuilds a TicTacToe from it. That keeps the server free of sessions,
so it scales to any number of tabs and survives restarts on Render.
"""

import os

from flask import Flask, jsonify, render_template, request

from agent import MinimaxAgent, create_agent, simulate_match
from game import TicTacToe, PLAYER_X, PLAYER_O, EMPTY

app = Flask(__name__)

AGENT_KINDS = ("random", "heuristic", "minimax")
MAX_SIM_GAMES = 1000


class BadRequest(Exception):
    pass


@app.errorhandler(BadRequest)
def handle_bad_request(err):
    return jsonify({"error": str(err)}), 400


def parse_game(data):
    """Build a TicTacToe from the JSON payload's 'board' (9 cells of 'X', 'O' or ' ')."""
    board = data.get("board")
    if not isinstance(board, list) or len(board) != 9:
        raise BadRequest("board must be a list of 9 cells")
    board = [cell if cell in (PLAYER_X, PLAYER_O) else EMPTY for cell in board]

    x_count, o_count = board.count(PLAYER_X), board.count(PLAYER_O)
    if x_count - o_count not in (0, 1):
        raise BadRequest("board has an impossible number of X and O marks")
    return TicTacToe(board=board)


def parse_kind(value, field):
    kind = str(value or "").lower()
    if kind in ("easy",):
        kind = "random"
    elif kind in ("medium",):
        kind = "heuristic"
    elif kind in ("hard", "unbeatable"):
        kind = "minimax"
    if kind not in AGENT_KINDS:
        raise BadRequest(f"{field} must be one of {', '.join(AGENT_KINDS)}")
    return kind


def build_agent(kind, player, alpha_beta=True):
    if kind == "minimax":
        return MinimaxAgent(player=player, use_alpha_beta=alpha_beta)
    return create_agent(kind, player)


def agent_stats(agent):
    """Per-move details for the visualizer, whatever kind of agent moved."""
    if isinstance(agent, MinimaxAgent):
        stats = agent.get_stats()
        # JSON object keys must be strings; the browser indexes by cell number.
        stats["move_scores"] = {str(k): v for k, v in stats["move_scores"].items()}
        return stats
    return {"rule": getattr(agent, "last_rule", None) or "random"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/move", methods=["POST"])
def human_move():
    """Apply a human move and return the resulting game state."""
    data = request.get_json(silent=True) or {}
    game = parse_game(data)
    pos = data.get("position")
    if not game.make_move(pos):
        raise BadRequest("illegal move")
    return jsonify({"position": pos, "state": game.to_dict()})


@app.route("/api/ai-move", methods=["POST"])
def ai_move():
    """Let an agent choose and play a move for the side to move."""
    data = request.get_json(silent=True) or {}
    game = parse_game(data)
    if game.is_game_over():
        raise BadRequest("game is already over")

    kind = parse_kind(data.get("agent"), "agent")
    agent = build_agent(kind, game.current_player, bool(data.get("alpha_beta", True)))
    player = game.current_player
    pos = agent.get_move(game)
    game.make_move(pos, player)

    return jsonify({
        "position": pos,
        "player": player,
        "agent": kind,
        "stats": agent_stats(agent),
        "state": game.to_dict(),
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Minimax evaluation of every legal move for the side to move, without playing."""
    data = request.get_json(silent=True) or {}
    game = parse_game(data)
    if game.is_game_over():
        return jsonify({"best_move": None, "stats": None})

    agent = MinimaxAgent(player=game.current_player,
                         use_alpha_beta=bool(data.get("alpha_beta", True)))
    best = agent.get_move(game)
    return jsonify({"best_move": best, "player": game.current_player,
                    "stats": agent_stats(agent)})


@app.route("/api/simulate", methods=["POST"])
def simulate():
    """Run a batch of bot-vs-bot games. agent1 plays X (moves first), agent2 plays O.

    The browser calls this repeatedly with small batches so the benchmark
    totals update live instead of waiting for one long request.
    """
    data = request.get_json(silent=True) or {}
    kind1 = parse_kind(data.get("agent1"), "agent1")
    kind2 = parse_kind(data.get("agent2"), "agent2")
    try:
        num_games = int(data.get("num_games", 10))
    except (TypeError, ValueError):
        raise BadRequest("num_games must be an integer") from None
    if not 1 <= num_games <= MAX_SIM_GAMES:
        raise BadRequest(f"num_games must be between 1 and {MAX_SIM_GAMES}")

    agent1 = build_agent(kind1, PLAYER_X)
    agent2 = build_agent(kind2, PLAYER_O)
    results = simulate_match(agent1, agent2, num_games)
    results.update({"agent1": kind1, "agent2": kind2})
    return jsonify(results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
