
from board.board import *
from algorithms.minimax import find_best_move


def play_game():
    board = create_board()
    current_player = HUMAN

    print("================================")
    print("       TIC-TAC-TOE")
    print("================================")
    print("Player 1 : Human (O)")
    print("Player 2 : AI (X) - Minimax")
    print("Pilih posisi 1-9 untuk bermain.")

    while not is_game_over(board):

        display_board(board)

        # Giliran Player 1 (Human)
        if current_player == HUMAN:

            print("Giliran Player 1 (Human)")

            try:
                position = int(input("Pilih posisi (1-9): ")) - 1
            except ValueError:
                print("Input harus berupa angka!")
                continue

            if make_move(board, position, HUMAN):
                current_player = AI
            else:
                print("Posisi tidak valid atau sudah terisi!")

        # Giliran Player 2 (AI Minimax)
        else:

            print("Giliran Player 2 (AI Minimax)")

            move, score = find_best_move(board, AI)

            if move is not None:
                make_move(board, move, AI)

                print(f"AI memilih posisi: {move + 1}")
                print(f"Skor Minimax: {score}")

            current_player = HUMAN

    # Menampilkan hasil akhir
    display_board(board)

    winner = check_winner(board)

    print("================================")

    if winner == HUMAN:
        print("Player 1 (Human) MENANG!")
    elif winner == AI:
        print("Player 2 (AI Minimax) MENANG!")
    else:
        print("PERMAINAN BERAKHIR DRAW!")

    print("================================")


if __name__ == "__main__":
    play_game()
