import random

def create_board(size=9):
    return [["." for _ in range(size)] for _ in range(size)]

def check_win(board, player):
    n = len(board)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for r in range(n):
        for c in range(n):
            if board[r][c] != player:
                continue
            for dr, dc in directions:
                count = 0
                for k in range(5):
                    nr, nc = r + dr * k, c + dc * k
                    if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == player:
                        count += 1
                    else:
                        break
                if count == 5:
                    return True
    return False

def is_full(board):
    return all(cell != "." for row in board for cell in row)

def switch_player(player):
    return "O" if player == "X" else "X"

