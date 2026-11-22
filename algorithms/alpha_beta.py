
import time
import tracemalloc

from board.board import (
    AI,
    HUMAN,
    EMPTY,
    get_available_moves,
    get_game_state
)


# Urutan prioritas posisi:
# Tengah -> Sudut -> Sisi
STRATEGIC_ORDER = [4, 0, 2, 6, 8, 1, 3, 5, 7]


def get_ordered_moves(board, move_order="standard"):
    """
    Mengembalikan langkah yang tersedia
    berdasarkan jenis urutan yang dipilih.
    """

    available_moves = get_available_moves(board)

    if move_order == "strategic":
        return [
            move for move in STRATEGIC_ORDER
            if move in available_moves
        ]

    return available_moves


def alpha_beta(
    board,
    depth,
    alpha,
    beta,
    maximizing,
    player,
    stats,
    move_order="standard"
):
    """
    Algoritma Alpha-Beta Pruning dengan
    pilihan urutan langkah.
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

    moves = get_ordered_moves(board, move_order)

    if maximizing:
        best_score = float("-inf")

        for move in moves:
            board[move] = player

            score = alpha_beta(
                board,
                depth + 1,
                alpha,
                beta,
                False,
                player,
                stats,
                move_order
            )

            board[move] = EMPTY

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if beta <= alpha:
                break

        return best_score

    else:
        best_score = float("inf")

        for move in moves:
            board[move] = opponent

            score = alpha_beta(
                board,
                depth + 1,
                alpha,
                beta,
                True,
                player,
                stats,
                move_order
            )

            board[move] = EMPTY

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            if beta <= alpha:
                break

        return best_score


def find_best_move(
    board,
    player=AI,
    move_order="standard"
):
    """
    Mencari langkah terbaik dan mengukur
    performa Alpha-Beta Pruning.
    """

    stats = {
        "nodes": 0,
        "execution_time_ms": 0,
        "peak_memory_kb": 0
    }

    available_moves = get_ordered_moves(
        board,
        move_order
    )

    if not available_moves:
        return None, 0, stats

    was_tracing = tracemalloc.is_tracing()

    if not was_tracing:
        tracemalloc.start()

    tracemalloc.reset_peak()
    baseline, _ = tracemalloc.get_traced_memory()

    start_time = time.perf_counter()

    best_score = float("-inf")
    best_move = None

    alpha = float("-inf")
    beta = float("inf")

    for move in available_moves:
        board[move] = player

        score = alpha_beta(
            board,
            0,
            alpha,
            beta,
            False,
            player,
            stats,
            move_order
        )

        board[move] = EMPTY

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, best_score)

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
