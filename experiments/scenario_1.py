
import csv
import os
import statistics

from board.board import (
    AI,
    HUMAN,
    EMPTY,
    get_available_moves,
    get_game_state
)

from algorithms.minimax import find_best_move as minimax
from algorithms.alpha_beta import find_best_move as alpha_beta


# ==========================================
# 1. KONFIGURASI PENGUJIAN
# ==========================================

REPEAT_TEST = 10

BOARD_STATES = [
    {
        "name": "Awal Permainan",
        "board": [
            EMPTY, EMPTY, EMPTY,
            EMPTY, EMPTY, EMPTY,
            EMPTY, EMPTY, EMPTY
        ]
    },
    {
        "name": "Pertengahan Permainan",
        "board": [
            AI, HUMAN, EMPTY,
            HUMAN, AI, EMPTY,
            EMPTY, EMPTY, EMPTY
        ]
    },
    {
        "name": "Akhir Permainan",
        "board": [
            AI, HUMAN, AI,
            HUMAN, EMPTY, HUMAN,
            AI, AI, EMPTY
        ]
    }
]


# ==========================================
# 2. MENAMPILKAN PAPAN
# ==========================================

def display_test_board(board):
    print()
    print(f" {board[0]} | {board[1]} | {board[2]}")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]}")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]}")
    print()


# ==========================================
# 3. MENJALANKAN PENGUJIAN ALGORITMA
# ==========================================

def run_algorithm(algorithm, board, player):
    execution_times = []
    memory_usages = []

    node_counts = []
    best_moves = []
    best_scores = []

    for _ in range(REPEAT_TEST):

        # Salinan papan agar kondisi awal tetap sama
        test_board = board.copy()

        move, score, stats = algorithm(
            test_board,
            player
        )

        node_counts.append(stats["nodes"])
        execution_times.append(
            stats["execution_time_ms"]
        )
        memory_usages.append(
            stats["peak_memory_kb"]
        )

        best_moves.append(move)
        best_scores.append(score)

    return {
        "nodes": statistics.mean(node_counts),
        "execution_time_ms": statistics.mean(execution_times),
        "peak_memory_kb": statistics.mean(memory_usages),
        "best_move": best_moves[0],
        "best_score": best_scores[0]
    }


# ==========================================
# 4. MENGHITUNG PRUNING RATIO
# ==========================================

def calculate_pruning_ratio(minimax_nodes, alpha_beta_nodes):

    if minimax_nodes == 0:
        return 0

    return (
        (minimax_nodes - alpha_beta_nodes)
        / minimax_nodes
    ) * 100


# ==========================================
# 5. MENJALANKAN SKENARIO 1
# ==========================================

def run_scenario_1():

    results = []

    print("=" * 55)
    print("SKENARIO 1: PENGUJIAN BERDASARKAN KEDALAMAN POHON")
    print("=" * 55)

    for index, scenario in enumerate(BOARD_STATES, start=1):

        board = scenario["board"]

        print(f"\nPENGUJIAN {index}: {scenario['name']}")
        print("-" * 55)

        display_test_board(board)

        empty_cells = len(get_available_moves(board))

        # Validasi kondisi papan
        if get_game_state(board) is not None:
            print("Papan tidak valid untuk pengujian.")
            continue

        # Kedua algoritma menggunakan pemain X
        player = AI

        print("Menjalankan Minimax...")
        minimax_result = run_algorithm(
            minimax,
            board,
            player
        )

        print("Menjalankan Alpha-Beta...")
        alpha_beta_result = run_algorithm(
            alpha_beta,
            board,
            player
        )

        pruning_ratio = calculate_pruning_ratio(
            minimax_result["nodes"],
            alpha_beta_result["nodes"]
        )

        # Menyimpan hasil pengujian
        result = {
            "scenario": scenario["name"],
            "empty_cells": empty_cells,

            "minimax_move": minimax_result["best_move"],
            "minimax_score": minimax_result["best_score"],
            "minimax_nodes": minimax_result["nodes"],
            "minimax_time_ms": minimax_result["execution_time_ms"],
            "minimax_memory_kb": minimax_result["peak_memory_kb"],

            "alpha_beta_move": alpha_beta_result["best_move"],
            "alpha_beta_score": alpha_beta_result["best_score"],
            "alpha_beta_nodes": alpha_beta_result["nodes"],
            "alpha_beta_time_ms": alpha_beta_result["execution_time_ms"],
            "alpha_beta_memory_kb": alpha_beta_result["peak_memory_kb"],

            "pruning_ratio_percent": pruning_ratio
        }

        results.append(result)

        # Menampilkan hasil
        print("\nHASIL PENGUJIAN")

        print("\nMinimax:")
        print(f"Jumlah Node       : {minimax_result['nodes']:.0f}")
        print(f"Waktu Eksekusi    : {minimax_result['execution_time_ms']:.6f} ms")
        print(f"Penggunaan Memori : {minimax_result['peak_memory_kb']:.4f} KB")
        print(f"Langkah Terbaik   : {minimax_result['best_move']}")

        print("\nAlpha-Beta Pruning:")
        print(f"Jumlah Node       : {alpha_beta_result['nodes']:.0f}")
        print(f"Waktu Eksekusi    : {alpha_beta_result['execution_time_ms']:.6f} ms")
        print(f"Penggunaan Memori : {alpha_beta_result['peak_memory_kb']:.4f} KB")
        print(f"Langkah Terbaik   : {alpha_beta_result['best_move']}")

        print(f"\nPruning Ratio     : {pruning_ratio:.2f}%")

    # ======================================
    # 6. MENYIMPAN HASIL KE CSV
    # ======================================

    output_path = os.path.join(
        os.path.dirname(__file__),
        "scenario_1_results.csv"
    )

    if results:
        with open(
            output_path,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=results[0].keys()
            )

            writer.writeheader()
            writer.writerows(results)

        print("\n" + "=" * 55)
        print("PENGUJIAN SKENARIO 1 SELESAI")
        print(f"Hasil disimpan di: {output_path}")
        print("=" * 55)


# ==========================================
# 7. PROGRAM UTAMA
# ==========================================

run_scenario_1()
