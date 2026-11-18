from .board import *

# TEST 1: Menang horizontal
board = create_board()
board[0] = HUMAN
board[1] = HUMAN
board[2] = HUMAN

print("TEST 1 - Horizontal")
display_board(board)
print("Pemenang:", check_winner(board))
print()

# TEST 2: Menang vertikal
board = create_board()
board[0] = AI
board[3] = AI
board[6] = AI

print("TEST 2 - Vertikal")
display_board(board)
print("Pemenang:", check_winner(board))
print()

# TEST 3: Menang diagonal
board = create_board()
board[0] = HUMAN
board[4] = HUMAN
board[8] = HUMAN

print("TEST 3 - Diagonal")
display_board(board)
print("Pemenang:", check_winner(board))
print()

# TEST 4: Draw
board = [
    HUMAN, AI, HUMAN,
    HUMAN, AI, AI,
    AI, HUMAN, AI
]

print("TEST 4 - Draw")
display_board(board)
print("Pemenang:", check_winner(board))
print("Draw:", is_draw(board))
print("Game selesai:", is_game_over(board))

# TEST 5: Invalid move
board = create_board()

make_move(board, 0, HUMAN)

print("TEST 5 - Invalid Move")

# Mencoba mengisi posisi yang sudah terisi
result1 = make_move(board, 0, AI)
print("Mengisi kotak yang sudah terisi:", result1)

# Mencoba posisi di luar board
result2 = make_move(board, 9, AI)
print("Posisi di luar board:", result2)

# Board setelah percobaan
display_board(board)