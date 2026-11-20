from board.board import (
    AI,
    HUMAN,
    EMPTY,
    get_available_moves,
    make_move,
    check_winner
)

def evaluate_board(board):
    """ Memberikan nilai berdasarkan kondisi papan.
        AI menang  : +10
        Human menang: -10
        Seri       : 0 """

    winner = check_winner(board)

    if winner == AI:
        return 10

    elif winner == HUMAN:
        return -10

    return 0


def alpha_beta(board, depth, alpha, beta, maximizing):
    """ Algoritma Alpha-Beta Pruning.
        maximizing = True  : giliran AI (X)
        maximizing = False : giliran Human (O)
        Mengembalikan nilai evaluasi terbaik. """

    score = evaluate_board(board)

    # Kondisi akhir permainan
    if score == 10:
        return score - depth

    if score == -10:
        return score + depth

    if not get_available_moves(board):
        return 0

    # Giliran AI (memaksimalkan nilai)
    if maximizing:
        best_score = float("-inf")

        for move in get_available_moves(board):
            board[move] = AI

            score = alpha_beta(
                board,
                depth + 1,
                alpha,
                beta,
                False
            )

            board[move] = EMPTY

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            # Alpha-Beta Pruning
            if beta <= alpha:
                break

        return best_score

    # Giliran Human (meminimalkan nilai)
    else:
        best_score = float("inf")

        for move in get_available_moves(board):
            board[move] = HUMAN

            score = alpha_beta(
                board,
                depth + 1,
                alpha,
                beta,
                True
            )

            board[move] = EMPTY

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            # Alpha-Beta Pruning
            if beta <= alpha:
                break

        return best_score


def find_best_move(board):
    """ Mencari posisi terbaik untuk AI.
        Mengembalikan indeks posisi 0-8. """

    best_score = float("-inf")
    best_move = None

    alpha = float("-inf")
    beta = float("inf")

    for move in get_available_moves(board):
        board[move] = AI

        score = alpha_beta(
            board,
            0,
            alpha,
            beta,
            False
        )

        board[move] = EMPTY

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, best_score)

    return best_move
