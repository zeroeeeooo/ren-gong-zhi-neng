from utils import check_win, switch_player
import random

def simple_bot(board, player):
    n = len(board)
    opponent = switch_player(player)

    # 1. 赢棋
    for r in range(n):
        for c in range(n):
            if board[r][c] == ".":
                board[r][c] = player
                if check_win(board, player):
                    board[r][c] = "."
                    return (r, c)
                board[r][c] = "."

    # 2. 堵棋
    for r in range(n):
        for c in range(n):
            if board[r][c] == ".":
                board[r][c] = opponent
                if check_win(board, opponent):
                    board[r][c] = "."
                    return (r, c)
                board[r][c] = "."

    # 3. 随机
    empty = [(r, c) for r in range(n) for c in range(n) if board[r][c] == "."]
    return random.choice(empty)
