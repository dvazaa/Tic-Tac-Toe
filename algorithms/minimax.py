
import os
import sys
import time
import tracemalloc

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from board.board import (
    AI,
    HUMAN,
    EMPTY,
    get_available_moves,
    get_game_state,
)


def minimax(board, depth, is_maximizing, player=AI, stats=None):
    """
    Algoritma Minimax.

    Skor:
    - Pemain sendiri menang : 10 - depth
    - Lawan menang           : depth - 10
    - Seri                   : 0
    """

    stats["nodes"] += 1

    opponent = HUMAN if player == AI else AI
    state = get_game_state(board)

    if state == player:
        return 10 - depth

    if state == opponent:
        return depth - 10

    if state == "draw":
        return 0

    if is_maximizing:
        best_score = -float("inf")

        for move in get_available_moves(board):
            board[move] = player

            score = minimax(
                board,
                depth + 1,
                False,
                player,
                stats
            )

            board[move] = EMPTY
            best_score = max(best_score, score)

        return best_score

    else:
        best_score = float("inf")

        for move in get_available_moves(board):
            board[move] = opponent

            score = minimax(
                board,
                depth + 1,
                True,
                player,
                stats
            )

            board[move] = EMPTY
            best_score = min(best_score, score)

        return best_score


def find_best_move(board, player=AI):
    """Mencari langkah terbaik dan mengukur performa Minimax."""

    stats = {
        "nodes": 0,
        "execution_time_ms": 0,
        "peak_memory_kb": 0
    }

    available_moves = get_available_moves(board)

    if not available_moves:
        return None, 0, stats

    was_tracing = tracemalloc.is_tracing()

    if not was_tracing:
        tracemalloc.start()

    tracemalloc.reset_peak()
    baseline, _ = tracemalloc.get_traced_memory()

    start_time = time.perf_counter()

    best_move = None
    best_score = -float("inf")

    for move in available_moves:
        board[move] = player

        score = minimax(
            board,
            0,
            False,
            player,
            stats
        )

        board[move] = EMPTY

        if score > best_score:
            best_score = score
            best_move = move

    end_time = time.perf_counter()

    _, peak_memory = tracemalloc.get_traced_memory()

    stats["execution_time_ms"] = (
        end_time - start_time
    ) * 1000

    stats["peak_memory_kb"] = (
        max(0, peak_memory - baseline) / 1024
    )

    if not was_tracing:
        tracemalloc.stop()

    return best_move, best_score, stats
