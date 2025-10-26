from utils import check_win, switch_player
import math

def evaluate(board, player):
    opponent = switch_player(player)
    scores = {2: 10, 3: 100, 4: 1000, 5: 100000}
    total_score = 0
    n = len(board)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    for r in range(n):
        for c in range(n):
            if board[r][c] == player:
                for dr, dc in directions:
                    count = 0
                    for k in range(5):
                        nr, nc = r + dr * k, c + dc * k
                        if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == player:
                            count += 1
                        else:
                            break
                    if count >= 2:
                        total_score += scores.get(count, 0)
            elif board[r][c] == opponent:
                for dr, dc in directions:
                    count = 0
                    for k in range(5):
                        nr, nc = r + dr * k, c + dc * k
                        if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == opponent:
                            count += 1
                        else:
                            break
                    if count >= 2:
                        total_score -= scores.get(count, 0)
    return total_score

def get_candidate_moves(board, distance=1):
    n = len(board)
    candidates = set()
    directions = [-distance, 0, distance]

    for r in range(n):
        for c in range(n):
            if board[r][c] != ".":
                for dr in directions:
                    for dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == ".":
                            candidates.add((nr, nc))
    return list(candidates) if candidates else [(n // 2, n // 2)]

def minimax(board, depth, alpha, beta, maximizing, player):
    opponent = switch_player(player)

    if depth == 0 or check_win(board, player) or check_win(board, opponent):
        return evaluate(board, player), None

    moves = get_candidate_moves(board, distance=1)
    best_move = None

    if maximizing:
        max_eval = -math.inf
        for r, c in moves:
            board[r][c] = player
            eval_score, _ = minimax(board, depth - 1, alpha, beta, False, player)
            board[r][c] = "."
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (r, c)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for r, c in moves:
            board[r][c] = opponent
            eval_score, _ = minimax(board, depth - 1, alpha, beta, True, player)
            board[r][c] = "."
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (r, c)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def minimax_aibot(board, player, depth=3):
    _, move = minimax(board, depth, -math.inf, math.inf, True, player)
    return move
