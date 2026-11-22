
from board.board import *
from algorithms.minimax import find_best_move as find_best_move_minimax
from algorithms.alpha_beta import find_best_move as find_best_move_alpha_beta


ALGORITHMS = {
    "1": ("Minimax", find_best_move_minimax),
    "2": ("Alpha-Beta Pruning", find_best_move_alpha_beta)
}


def choose_algorithm(player):
    print(f"\nPilih algoritma {player}:")
    print("1. Minimax")
    print("2. Alpha-Beta Pruning")

    choice = input("Pilih algoritma (1-2): ")

    if choice not in ALGORITHMS:
        print("Pilihan tidak valid!")
        return None

    return ALGORITHMS[choice]


def display_stats(stats, algorithm_name):
    print(f"\n--- Statistik Performa {algorithm_name} ---")
    print(f"Jumlah Node          : {stats['nodes']}")
    print(f"Waktu Eksekusi       : {stats['execution_time_ms']:.4f} ms")
    print(f"Peak Memory Usage    : {stats['peak_memory_kb']:.4f} KB")


def play_game():

    board = create_board()

    print("================================")
    print("          TIC-TAC-TOE")
    print("================================")

    print("\nPilih mode permainan:")
    print("1. Human vs Human")
    print("2. Human vs AI")
    print("3. AI vs AI")

    mode = input("Pilih mode (1-3): ")

    if mode not in ["1", "2", "3"]:
        print("Pilihan tidak valid!")
        return

    players = {}

    if mode == "1":
        players[HUMAN] = ("Human", None)
        players[AI] = ("Human", None)

    elif mode == "2":
        players[HUMAN] = ("Human", None)

        algorithm = choose_algorithm("AI")

        if algorithm is None:
            return

        players[AI] = algorithm

    elif mode == "3":
        algorithm1 = choose_algorithm("Player 1")

        if algorithm1 is None:
            return

        algorithm2 = choose_algorithm("Player 2")

        if algorithm2 is None:
            return

        players[HUMAN] = algorithm1
        players[AI] = algorithm2

    current_player = HUMAN

    print("\n================================")
    print("Player 1 :", players[HUMAN][0], "(O)")
    print("Player 2 :", players[AI][0], "(X)")
    print("================================")

    while not is_game_over(board):

        display_board(board)

        player_name, algorithm = players[current_player]

        if algorithm is None:

            print(f"\nGiliran {player_name}")

            try:
                position = int(input("Pilih posisi (1-9): ")) - 1
            except ValueError:
                print("Input harus berupa angka!")
                continue

            if make_move(board, position, current_player):
                current_player = (
                    AI if current_player == HUMAN else HUMAN
                )
            else:
                print("Posisi tidak valid atau sudah terisi!")

        else:

            print(f"\nGiliran {player_name} ({current_player})")
            print("AI sedang berpikir...")

            move, score, stats = algorithm(
                board,
                current_player
            )

            if move is not None:
                make_move(board, move, current_player)

                print(f"AI memilih posisi: {move + 1}")
                print(f"Skor: {score}")

                display_stats(stats, player_name)

            current_player = (
                AI if current_player == HUMAN else HUMAN
            )

    display_board(board)

    winner = check_winner(board)

    print("\n================================")

    if winner == HUMAN:
        print(f"Player 1 ({players[HUMAN][0]}) MENANG!")

    elif winner == AI:
        print(f"Player 2 ({players[AI][0]}) MENANG!")

    else:
        print("PERMAINAN BERAKHIR DRAW!")

    print("================================")


if __name__ == "__main__":
    play_game()
