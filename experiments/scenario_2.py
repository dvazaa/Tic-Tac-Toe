
import os
import sys
import csv
import statistics

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from board.board import (
    AI,
    HUMAN,
    EMPTY,
    get_available_moves,
    get_game_state
)

from algorithms.alpha_beta import find_best_move


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
# 3. MENJALANKAN PENGUJIAN
# ==========================================

def run_ordering_test(board, move_order):

    nodes = []
    times = []
    memories = []
    moves = []
    scores = []

    for _ in range(REPEAT_TEST):

        test_board = board.copy()

        move, score, stats = find_best_move(
            test_board,
            AI,
            move_order
        )

        nodes.append(stats["nodes"])
        times.append(stats["execution_time_ms"])
        memories.append(stats["peak_memory_kb"])

        moves.append(move)
        scores.append(score)

    return {
        "nodes": statistics.mean(nodes),
        "time_ms": statistics.mean(times),
        "memory_kb": statistics.mean(memories),
        "best_move": moves[0],
        "best_score": scores[0]
    }


# ==========================================
# 4. MENJALANKAN SKENARIO 2
# ==========================================

def run_scenario_2():

    results = []

    print("=" * 60)
    print("SKENARIO 2: PENGUJIAN MOVE ORDERING")
    print("=" * 60)

    for index, scenario in enumerate(BOARD_STATES, start=1):

        board = scenario["board"]

        print(f"\nPENGUJIAN {index}: {scenario['name']}")
        print("-" * 60)

        display_test_board(board)

        if get_game_state(board) is not None:
            print("Papan tidak valid untuk pengujian.")
            continue

        print("Menjalankan Alpha-Beta Standard...")
        standard = run_ordering_test(
            board,
            "standard"
        )

        print("Menjalankan Alpha-Beta Strategic...")
        strategic = run_ordering_test(
            board,
            "strategic"
        )

        # Menghitung pengurangan node
        if standard["nodes"] > 0:
            node_reduction = (
                (standard["nodes"] - strategic["nodes"])
                / standard["nodes"]
            ) * 100
        else:
            node_reduction = 0

        result = {
            "scenario": scenario["name"],
            "empty_cells": len(get_available_moves(board)),

            "standard_nodes": standard["nodes"],
            "standard_time_ms": standard["time_ms"],
            "standard_memory_kb": standard["memory_kb"],
            "standard_move": standard["best_move"],
            "standard_score": standard["best_score"],

            "strategic_nodes": strategic["nodes"],
            "strategic_time_ms": strategic["time_ms"],
            "strategic_memory_kb": strategic["memory_kb"],
            "strategic_move": strategic["best_move"],
            "strategic_score": strategic["best_score"],

            "node_reduction_percent": node_reduction
        }

        results.append(result)

        # Menampilkan hasil pengujian
        print("\nHASIL STANDARD ORDERING")
        print(f"Jumlah Node       : {standard['nodes']:.0f}")
        print(f"Waktu Eksekusi    : {standard['time_ms']:.6f} ms")
        print(f"Penggunaan Memori : {standard['memory_kb']:.4f} KB")
        print(f"Langkah Terbaik   : {standard['best_move']}")
        print(f"Skor              : {standard['best_score']}")

        print("\nHASIL STRATEGIC ORDERING")
        print(f"Jumlah Node       : {strategic['nodes']:.0f}")
        print(f"Waktu Eksekusi    : {strategic['time_ms']:.6f} ms")
        print(f"Penggunaan Memori : {strategic['memory_kb']:.4f} KB")
        print(f"Langkah Terbaik   : {strategic['best_move']}")
        print(f"Skor              : {strategic['best_score']}")

        print(
            f"\nPengurangan Node : {node_reduction:.2f}%"
        )

        if standard["best_score"] != strategic["best_score"]:
            print(
                "PERINGATAN: Skor kedua metode berbeda!"
            )

    # ======================================
    # 5. MENYIMPAN HASIL KE CSV
    # ======================================

    output_path = os.path.join(
        os.path.dirname(__file__),
        "scenario_2_results.csv"
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

        print("\n" + "=" * 60)
        print("PENGUJIAN SKENARIO 2 SELESAI")
        print(f"Hasil disimpan di: {output_path}")
        print("=" * 60)


# ==========================================
# 6. PROGRAM UTAMA
# ==========================================

run_scenario_2()
