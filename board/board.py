# board.py

# Simbol pemain
HUMAN = "O"
AI = "X"
EMPTY = " "


def create_board():
    """
    Membuat papan permainan kosong dengan 9 posisi.
    """
    return [EMPTY] * 9


def display_board(board):
    """
    Menampilkan papan Tic-Tac-Toe.
    Posisi ditampilkan dengan nomor 1-9
    jika petak masih kosong.
    """

    cells = []

    for i in range(9):
        if board[i] == EMPTY:
            cells.append(str(i + 1))
        else:
            cells.append(board[i])

    print()
    print(f" {cells[0]} | {cells[1]} | {cells[2]}")
    print("---+---+---")
    print(f" {cells[3]} | {cells[4]} | {cells[5]}")
    print("---+---+---")
    print(f" {cells[6]} | {cells[7]} | {cells[8]}")
    print()


def get_available_moves(board):
    """
    Mengembalikan daftar indeks posisi yang masih kosong.
    """

    return [
        i for i in range(9)
        if board[i] == EMPTY
    ]


def make_move(board, position, player):
    """
    Melakukan langkah pemain jika posisi valid
    dan masih kosong.

    position menggunakan indeks 0-8.
    """

    if position < 0 or position > 8:
        return False

    if board[position] != EMPTY:
        return False

    if player not in [HUMAN, AI]:
        return False

    board[position] = player

    return True


def check_winner(board):
    """
    Mengecek apakah terdapat pemenang.

    Mengembalikan:
    - "X" jika AI menang
    - "O" jika Human menang
    - None jika belum ada pemenang
    """

    winning_combinations = [
        # Baris
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],

        # Kolom
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],

        # Diagonal
        [0, 4, 8],
        [2, 4, 6]
    ]

    for combination in winning_combinations:

        a, b, c = combination

        if (
            board[a] != EMPTY
            and board[a] == board[b]
            and board[b] == board[c]
        ):
            return board[a]

    return None


def is_draw(board):
    """
    Mengecek apakah permainan berakhir seri.
    """

    return (
        check_winner(board) is None
        and EMPTY not in board
    )


def is_game_over(board):
    """
    Mengecek apakah permainan sudah berakhir,
    baik karena menang maupun seri.
    """

    return (
        check_winner(board) is not None
        or is_draw(board)
    )


def get_game_state(board):
    """
    Mengembalikan kondisi permainan.

    Hasil:
    - "X" jika AI menang
    - "O" jika Human menang
    - "draw" jika seri
    - None jika permainan masih berlangsung
    """

    winner = check_winner(board)

    if winner is not None:
        return winner

    if is_draw(board):
        return "draw"

    return None