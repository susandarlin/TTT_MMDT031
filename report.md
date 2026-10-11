# Project 2 Report: Adversarial Search & Tic-Tac-Toe AI

> [!IMPORTANT]
> **AUTOGRADER COMPLIANCE INSTRUCTIONS:**
> This report is parsed automatically by the autograder. To ensure you receive full credit for your work:
> 1. **Do not modify** the section headers (`## ...`) or bold field keys (e.g., `**Name:**`, `**Primary AI Algorithm:**`, `**Live Deployment URL:**`, etc.).
> 2. **Write your answers directly after** the colon `:` of each field, replacing the placeholder text completely (including the outer brackets `[` and `]`).
> 3. **Maintain the file structure**. Changing headers, bold titles, or deleting lines can cause the autograder to miss your responses and award 0 marks.

---

## Student Information
- **Name:** Su Sandar Lin
- **MMDT ID:** MMDT031

---

## Section 1: AI Agent Configuration
- **Primary AI Algorithm:** Full-depth Minimax search with Alpha-Beta Pruning (MinimaxAgent, plays the "Hard/Unbeatable" difficulty)
- **Pruning Technique:** Alpha-Beta Pruning with Depth Penalty (cut off a branch once alpha >= beta; terminal scores are +10 - depth for a win, depth - 10 for a loss, 0 for a draw, so the agent prefers faster wins and slower losses)
- **Heuristic Strategy:** Win > Block > Center > Corners > Edges (HeuristicAgent: take an immediate win, otherwise block the opponent's immediate win, otherwise take the center, then a random free corner, then a random free edge)

---

## Section 2: Complexity & Search Tree Analysis
- **Maximum Search Depth (Empty 3x3 Board):** 9
- **Total Possible Board States:** 5,478 legal reachable board states (including the empty board; 765 after removing rotations and reflections)
- **Unbeatable Minimax Guarantee:** Yes

---

## Section 3: Local Verification & Agent Checklist
*Check the algorithms, agents, and features you successfully ran and verified on your local development server by placing an `x` in the brackets (e.g., `[x]`):*
- [x] Minimax Search Algorithm with Depth Penalty
- [x] Alpha-Beta Pruning Optimization
- [x] Rule-Based Heuristic Agent
- [x] Uniform Random Baseline Agent
- [x] Interactive Web Visualizer with Move Matrix & Metrics
- [x] Bot vs Bot Simulation Benchmark

---

## Section 4: Deployed and Presentation Information
- **Deployment Platform:** Render
- **Live Deployment URL:** [Provide your live deployment site URL here]
- **Video Presentation Link:** [Provide an accessible link to your 5–7 minute video presentation]

---

## Section 5: Discussion
*Provide your written analysis for each point by replacing the bracket placeholders below:*
- **Explain how Alpha-Beta pruning reduces the number of evaluated game tree nodes without changing the minimax decision.**
    Alpha-Beta pruning keeps two bounds during the Minimax search. Alpha is the best score the maximizing player (our agent) is already guaranteed, and beta is the best score the minimizing player (the opponent) is already guaranteed. When a node's bounds cross (alpha >= beta), the rest of that node's children are skipped. A rational player higher up the tree would never let the game reach that node, because they already have a better option elsewhere. For example, if the maximizer already has a move worth 0 (a draw) and the opponent's first reply in another branch forces -9 (a loss), the remaining replies in that branch don't need to be searched: the opponent can already push the score down to -9 or lower, so the maximizer will never pick that branch. Only branches that cannot affect the final choice are skipped, so the root gets exactly the same Minimax value and the same chosen move. The saving depends on move ordering. With good ordering, the number of nodes drops from O(b^d) to about O(b^(d/2)), which roughly doubles the depth that can be searched in the same time. In my implementation, an opening move from the empty board visits 549,945 nodes with plain Minimax but only 34,202 with Alpha-Beta (about 94% fewer), and both choose a move with the same score. Each root move is searched with a full window, so the per-move scores shown in the visualizer are still exact.
- **Compare classical Adversarial Search (Minimax / Alpha-Beta) with modern Tree Search approaches in Generative AI (e.g., Monte Carlo Tree Search, Tree of Thoughts, or Process Reward Models).**
    Classical Minimax / Alpha-Beta is a deterministic, exhaustive (or depth-limited) search. It needs a small, fully known set of legal moves, exact rules for applying them, and terminal utilities (or a hand-made evaluation function). Under those conditions it is provably optimal, which is why it plays Tic-Tac-Toe perfectly. It doesn't scale to huge branching factors such as Go or natural language, and it can't handle actions it cannot list out. Monte Carlo Tree Search (MCTS) replaces exhaustive search with sampling. It repeats four steps: select a node with the UCT/UCB1 formula (balancing exploration and exploitation), expand it, simulate (or estimate the outcome with a neural value network, as in AlphaGo/AlphaZero), and backpropagate the result. It spends more effort on promising branches, can be stopped at any time, and gets closer to the optimal choice the longer it runs. In Generative AI, the same idea of searching over a tree is applied to reasoning: Tree of Thoughts treats partial chains of reasoning ("thoughts") as nodes. An LLM proposes the next steps and evaluates them, and the search runs as BFS, DFS, or beam search with backtracking. Process Reward Models (PRMs) score each intermediate reasoning step instead of only the final answer. That gives the search a learned evaluation function, much like a heuristic in depth-limited Minimax, which can guide beam search, best-of-N selection, or MCTS over reasoning paths. The main differences: (1) Minimax assumes an adversarial opponent and works out the worst case, while LLM tree search usually optimizes against a reward or verifier rather than an opponent. (2) Minimax uses exact rules and true utilities, while modern methods rely on learned, noisy value estimates (value networks, LLM self-evaluation, PRMs). (3) Minimax searches every possibility and is guaranteed optimal, while MCTS/ToT sample from a practically unlimited space and trade guarantees for scalability. The shared idea is to search ahead over a tree of possible actions, judge each one with an evaluation function, and prune or ignore branches that don't look promising. Alpha-Beta's pruning and depth penalty are early versions of the value-guided search that powers today's reasoning models.
