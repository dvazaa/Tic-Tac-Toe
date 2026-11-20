import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from board.board import (
    AI,
    EMPTY,
    HUMAN,
    get_available_moves,
    get_game_state,
)


def minimax(board, depth, is_maximizing):
    """
    Algoritma Minimax untuk mengevaluasi posisi papan Tic-Tac-Toe.

    Skor:
    - AI ("X") menang    : 10 - depth (lebih cepat menang = skor lebih tinggi)
    - Human ("O") menang : depth - 10 (lebih lambat kalah = skor lebih baik)
    - Seri ("draw")      : 0
    """
    state = get_game_state(board)

    if state == AI:
        return 10 - depth
    if state == HUMAN:
        return depth - 10
    if state == "draw":
        return 0

    if is_maximizing:
        best_score = -float("inf")
        for move in get_available_moves(board):
            board[move] = AI
            score = minimax(board, depth + 1, False)
            board[move] = EMPTY
            if score > best_score:
                best_score = score
        return best_score
    else:
        best_score = float("inf")
        for move in get_available_moves(board):
            board[move] = HUMAN
            score = minimax(board, depth + 1, True)
            board[move] = EMPTY
            if score < best_score:
                best_score = score
        return best_score


def find_best_move(board, player=AI):
    # """
    # Mencari langkah terbaik untuk pemain tertentu menggunakan Minimax.

    # Mengembalikan tuple (best_move, best_score):
    # - best_move  : indeks posisi terbaik (0-8), atau None jika tidak ada langkah
    # - best_score : skor minimax dari langkah terbaik
    # """
    available_moves = get_available_moves(board)
    if not available_moves:
        return None, 0

    is_maximizing = player == AI
    best_move = None
    best_score = -float("inf") if is_maximizing else float("inf")

    for move in available_moves:
        board[move] = player
        score = minimax(board, 0, not is_maximizing)
        board[move] = EMPTY

        if is_maximizing and score > best_score:
            best_score = score
            best_move = move
        elif not is_maximizing and score < best_score:
            best_score = score
            best_move = move

    return best_move, best_score
