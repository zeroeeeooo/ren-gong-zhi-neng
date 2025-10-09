import random

def random_bot(board, player):
    n = len(board)
    empty = [(r, c) for r in range(n) for c in range(n) if board[r][c] == "."]
    return random.choice(empty)
