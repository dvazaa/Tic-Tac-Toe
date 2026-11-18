from board.board import *


def play_game():
    board = create_board()
    current_player = HUMAN

    print("Tic-Tac-Toe")
    print("Pilih posisi 1-9 untuk bermain.")
    print("Player O dan Player X bermain bergantian.")

    while not is_game_over(board):
        display_board(board)

        print(f"Giliran {current_player}")

        try:
            position = int(input("Pilih posisi (1-9): ")) - 1
        except ValueError:
            print("Input harus berupa angka!")
            continue

        if make_move(board, position, current_player):
            if current_player == HUMAN:
                current_player = AI
            else:
                current_player = HUMAN
        else:
            print("Posisi tidak valid atau sudah terisi!")

    display_board(board)

    winner = check_winner(board)

    if winner is not None:
        print(f"Player {winner} menang!")
    else:
        print("Permainan berakhir Draw!")


if __name__ == "__main__":
    play_game()