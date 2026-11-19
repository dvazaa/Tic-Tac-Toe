# tes.py

import os
import sys

# Menambahkan folder saat ini dan root proyek ke sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

for path in (CURRENT_DIR, ROOT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from board.board import (
    AI,
    EMPTY,
    HUMAN,
    check_winner,
    create_board,
    display_board,
    is_game_over,
    make_move,
)
from minimax import find_best_move


def run_tests():
    # TEST 1: AI mengambil langkah menang langsung
    print("=" * 40)
    print("TEST 1 - AI Menang Langsung")
    board = [
        AI, AI, EMPTY,
        HUMAN, HUMAN, EMPTY,
        EMPTY, EMPTY, EMPTY,
    ]
    print("Papan sebelum langkah AI:")
    display_board(board)
    move, score = find_best_move(board, AI)
    print(f"Langkah terbaik AI: posisi {move + 1} (indeks {move}), skor: {score}")
    assert move == 2, f"Seharusnya memilih indeks 2 (posisi 3), malah memilih {move}"
    make_move(board, move, AI)
    display_board(board)

    # TEST 2: AI memblokir ancaman menang Human
    print("=" * 40)
    print("TEST 2 - AI Memblokir Human")
    board = [
        HUMAN, HUMAN, EMPTY,
        EMPTY, AI, EMPTY,
        EMPTY, EMPTY, EMPTY,
    ]
    print("Papan sebelum langkah AI:")
    display_board(board)
    move, score = find_best_move(board, AI)
    print(f"Langkah terbaik AI: posisi {move + 1} (indeks {move}), skor: {score}")
    assert move == 2, f"Seharusnya memblokir indeks 2 (posisi 3), malah memilih {move}"
    make_move(board, move, AI)
    display_board(board)

    # TEST 3: AI merespons langkah pojok Human dengan mengambil tengah
    print("=" * 40)
    print("TEST 3 - Respons Langkah Awal (Human di Pojok)")
    board = create_board()
    make_move(board, 0, HUMAN)
    print("Papan sebelum langkah AI:")
    display_board(board)
    move, score = find_best_move(board, AI)
    print(f"Langkah terbaik AI: posisi {move + 1} (indeks {move}), skor: {score}")
    assert move == 4, f"Seharusnya mengambil tengah indeks 4 (posisi 5), malah memilih {move}"
    make_move(board, move, AI)
    display_board(board)

    # TEST 4: Simulasi Minimax vs Minimax (harus berakhir Draw)
    print("=" * 40)
    print("TEST 4 - Simulasi Minimax (O) vs Minimax (X)")
    board = create_board()
    current_player = HUMAN

    while not is_game_over(board):
        move, score = find_best_move(board, current_player)
        make_move(board, move, current_player)
        print(f"Player {current_player} memilih posisi {move + 1} (skor: {score})")
        current_player = AI if current_player == HUMAN else HUMAN

    display_board(board)
    winner = check_winner(board)
    print("Hasil akhir:", f"Player {winner} menang" if winner else "Draw")
    assert winner is None, f"Permainan optimal seharusnya Draw, tetapi {winner} menang"

    print("=" * 40)
    print("Semua uji coba Minimax berhasil!")


if __name__ == "__main__":
    run_tests()
