
import os
import sys
import csv
import random
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
    create_board,
    get_available_moves,
    get_game_state
)

from algorithms.minimax import find_best_move as minimax
from algorithms.alpha_beta import find_best_move as alpha_beta


# ==========================================
# 1. KONFIGURASI PENGUJIAN
# ==========================================

TOTAL_ROUNDS = 20
ROUNDS_PER_SIDE = TOTAL_ROUNDS // 2

ALGORITHMS = {
    "Minimax": minimax,
    "Alpha-Beta": alpha_beta
}


# ==========================================
# 2. RANDOM AGENT
# ==========================================

def random_agent(board, player, rng):
    """
    Memilih langkah secara acak dari
    posisi yang masih tersedia.
    """

    available_moves = get_available_moves(board)

    if not available_moves:
        return None

    return rng.choice(available_moves)


# ==========================================
# 3. MENJALANKAN SATU PERMAINAN
# ==========================================

def play_game(x_agent, o_agent, seed):
    """
    Menjalankan satu permainan Tic-Tac-Toe.

    x_agent : agen yang bermain sebagai X
    o_agent : agen yang bermain sebagai O
    """

    board = create_board()
    rng = random.Random(seed)

    current_player = AI

    # Statistik pencarian setiap algoritma
    metrics = {}

    while get_game_state(board) is None:

        if current_player == AI:
            agent = x_agent
        else:
            agent = o_agent

        agent_name = agent["name"]

        if agent_name == "Random":
            move = random_agent(
                board,
                current_player,
                rng
            )

        else:
            algorithm = agent["function"]

            move, score, stats = algorithm(
                board,
                current_player
            )

            if agent_name not in metrics:
                metrics[agent_name] = {
                    "nodes": [],
                    "times": [],
                    "memories": [],
                    "moves": 0
                }

            metrics[agent_name]["nodes"].append(
                stats["nodes"]
            )

            metrics[agent_name]["times"].append(
                stats["execution_time_ms"]
            )

            metrics[agent_name]["memories"].append(
                stats["peak_memory_kb"]
            )

            metrics[agent_name]["moves"] += 1

        if move is None or move not in get_available_moves(board):
            raise RuntimeError(
                f"{agent_name} menghasilkan langkah tidak valid."
            )

        board[move] = current_player

        if get_game_state(board) is not None:
            break

        current_player = (
            HUMAN if current_player == AI else AI
        )

    winner = get_game_state(board)

    if winner == AI:
        winner_name = x_agent["name"]

    elif winner == HUMAN:
        winner_name = o_agent["name"]

    else:
        winner_name = "Draw"

    return {
        "winner": winner,
        "winner_name": winner_name,
        "metrics": metrics
    }


# ==========================================
# 4. MENGHITUNG HASIL PERMAINAN
# ==========================================

def get_result(agent_name, winner_name):

    if winner_name == "Draw":
        return "Draw"

    if winner_name == agent_name:
        return "Win"

    return "Loss"


def calculate_percentage(value, total):

    if total == 0:
        return 0

    return (value / total) * 100


# ==========================================
# 5. MENYIAPKAN DATA METRIK
# ==========================================

def get_metric_values(metrics, agent_name):

    data = metrics.get(agent_name)

    if not data or data["moves"] == 0:
        return {
            "nodes": 0,
            "time_ms": 0,
            "memory_kb": 0,
            "moves": 0
        }

    return {
        "nodes": statistics.mean(data["nodes"]),
        "time_ms": statistics.mean(data["times"]),
        "memory_kb": statistics.mean(data["memories"]),
        "moves": data["moves"]
    }


# ==========================================
# 6. PENGUJIAN MELAWAN RANDOM AGENT
# ==========================================

def run_random_matches(on_round=None):

    game_results = []
    summary = {}

    print("\n" + "=" * 65)
    print("PENGUJIAN MELAWAN RANDOM AGENT")
    print("=" * 65)

    for algorithm_name, algorithm in ALGORITHMS.items():

        summary[algorithm_name] = {
            "Win": 0,
            "Draw": 0,
            "Loss": 0
        }

        print(f"\nAlgoritma: {algorithm_name}")

        for game_number in range(1, TOTAL_ROUNDS + 1):

            # 10 kali X, kemudian 10 kali O
            if game_number <= ROUNDS_PER_SIDE:
                x_agent = {
                    "name": algorithm_name,
                    "function": algorithm
                }

                o_agent = {
                    "name": "Random"
                }

            else:
                x_agent = {
                    "name": "Random"
                }

                o_agent = {
                    "name": algorithm_name,
                    "function": algorithm
                }

            result = play_game(
                x_agent,
                o_agent,
                seed=1000 + game_number
            )

            outcome = get_result(
                algorithm_name,
                result["winner_name"]
            )

            summary[algorithm_name][outcome] += 1

            metrics = get_metric_values(
                result["metrics"],
                algorithm_name
            )

            game_results.append({
                "mode": "Vs Random",
                "algorithm": algorithm_name,
                "game": game_number,
                "x_agent": x_agent["name"],
                "o_agent": o_agent["name"],
                "winner": result["winner_name"],
                "result": outcome,
                "algorithm_moves": metrics["moves"],
                "average_nodes": metrics["nodes"],
                "average_time_ms": metrics["time_ms"],
                "average_memory_kb": metrics["memory_kb"]
            })

            print(
                f"Ronde {game_number:02d} | "
                f"X: {x_agent['name']} | "
                f"O: {o_agent['name']} | "
                f"Hasil: {outcome}"
            )

            if on_round is not None:
                on_round(algorithm_name, game_number, TOTAL_ROUNDS, list(game_results))

        print_summary(
            algorithm_name,
            summary[algorithm_name]
        )

    return game_results, summary


# ==========================================
# 7. PERTANDINGAN MINIMAX VS ALPHA-BETA
# ==========================================

def run_direct_matches(on_round=None):

    game_results = []

    summary = {
        "Minimax": {
            "Win": 0,
            "Draw": 0,
            "Loss": 0
        },
        "Alpha-Beta": {
            "Win": 0,
            "Draw": 0,
            "Loss": 0
        }
    }

    print("\n" + "=" * 65)
    print("PERTANDINGAN MINIMAX VS ALPHA-BETA")
    print("=" * 65)

    for game_number in range(1, TOTAL_ROUNDS + 1):

        if game_number <= ROUNDS_PER_SIDE:
            x_name = "Minimax"
            o_name = "Alpha-Beta"
        else:
            x_name = "Alpha-Beta"
            o_name = "Minimax"

        x_agent = {
            "name": x_name,
            "function": ALGORITHMS[x_name]
        }

        o_agent = {
            "name": o_name,
            "function": ALGORITHMS[o_name]
        }

        result = play_game(
            x_agent,
            o_agent,
            seed=2000 + game_number
        )

        minimax_result = get_result(
            "Minimax",
            result["winner_name"]
        )

        alpha_result = get_result(
            "Alpha-Beta",
            result["winner_name"]
        )

        summary["Minimax"][minimax_result] += 1
        summary["Alpha-Beta"][alpha_result] += 1

        minimax_metrics = get_metric_values(
            result["metrics"],
            "Minimax"
        )

        alpha_metrics = get_metric_values(
            result["metrics"],
            "Alpha-Beta"
        )

        game_results.append({
            "mode": "Direct Match",
            "game": game_number,
            "x_agent": x_name,
            "o_agent": o_name,
            "winner": result["winner_name"],

            "minimax_result": minimax_result,
            "minimax_moves": minimax_metrics["moves"],
            "minimax_nodes": minimax_metrics["nodes"],
            "minimax_time_ms": minimax_metrics["time_ms"],
            "minimax_memory_kb": minimax_metrics["memory_kb"],

            "alpha_beta_result": alpha_result,
            "alpha_beta_moves": alpha_metrics["moves"],
            "alpha_beta_nodes": alpha_metrics["nodes"],
            "alpha_beta_time_ms": alpha_metrics["time_ms"],
            "alpha_beta_memory_kb": alpha_metrics["memory_kb"]
        })

        print(
            f"Ronde {game_number:02d} | "
            f"X: {x_name} | "
            f"O: {o_name} | "
            f"Pemenang: {result['winner_name']}"
        )

        if on_round is not None:
            on_round(game_number, TOTAL_ROUNDS, list(game_results))

    print("\nHASIL MINIMAX")
    print_summary("Minimax", summary["Minimax"])

    print("\nHASIL ALPHA-BETA")
    print_summary("Alpha-Beta", summary["Alpha-Beta"])

    return game_results, summary


# ==========================================
# 8. MENAMPILKAN RINGKASAN
# ==========================================

def print_summary(name, results):

    total = sum(results.values())

    print(f"\nRingkasan {name}")
    print(f"Menang : {results['Win']}")
    print(f"Seri   : {results['Draw']}")
    print(f"Kalah  : {results['Loss']}")

    print(
        f"Win Rate  : {calculate_percentage(results['Win'], total):.2f}%"
    )

    print(
        f"Draw Rate : {calculate_percentage(results['Draw'], total):.2f}%"
    )

    print(
        f"Loss Rate : {calculate_percentage(results['Loss'], total):.2f}%"
    )


# ==========================================
# 9. MENYIMPAN HASIL KE CSV
# ==========================================

def save_csv(filename, results):

    if not results:
        return

    output_path = os.path.join(
        os.path.dirname(__file__),
        filename
    )

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

    print(f"\nHasil tersimpan: {output_path}")


# ==========================================
# 10. PROGRAM UTAMA
# ==========================================

def run_scenario_3(on_progress=None):

    total_rounds = TOTAL_ROUNDS * (len(ALGORITHMS) + 1)
    completed = 0
    latest_random = []
    latest_direct = []

    def _on_random_round(algo_name, game_number, total, rows):
        nonlocal completed, latest_random
        completed += 1
        latest_random = rows
        if on_progress is not None:
            on_progress({
                "stage": f"{algo_name} vs Random: Ronde {game_number}/{total}",
                "progress": completed / total_rounds,
                "random_rows": rows,
                "direct_rows": latest_direct,
            })

    def _on_direct_round(game_number, total, rows):
        nonlocal completed, latest_direct
        completed += 1
        latest_direct = rows
        if on_progress is not None:
            on_progress({
                "stage": f"Minimax vs Alpha-Beta: Ronde {game_number}/{total}",
                "progress": completed / total_rounds,
                "random_rows": latest_random,
                "direct_rows": rows,
            })

    random_results, random_summary = run_random_matches(on_round=_on_random_round)

    direct_results, direct_summary = run_direct_matches(on_round=_on_direct_round)

    save_csv(
        "scenario_3_random_results.csv",
        random_results
    )

    save_csv(
        "scenario_3_direct_results.csv",
        direct_results
    )

    print("\n" + "=" * 65)
    print("SELURUH PENGUJIAN SKENARIO 3 SELESAI")
    print("=" * 65)


if __name__ == "__main__":
    run_scenario_3()
