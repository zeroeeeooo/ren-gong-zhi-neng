from bots.utils import create_board, check_win, is_full, switch_player
from bots.random_bot import random_bot
from bots.simple_bot import simple_bot
from bots.minimax_bot import minimax_bot

def bot_vs_bot(bot1, bot2, board_size=9, depth=3):
    board = create_board(board_size)
    current_player = "X"
    bots = {"X": bot1, "O": bot2}

    while True:
        if bots[current_player] == minimax_bot:
            move = bots[current_player](board, current_player, depth=depth)
        else:
            move = bots[current_player](board, current_player)

        row, col = move
        board[row][col] = current_player

        if check_win(board, current_player):
            return current_player
        if is_full(board):
            return "draw"

        current_player = switch_player(current_player)

def test_bots(bot1, bot2, rounds=20):
    results = {"X": 0, "O": 0, "draw": 0}
    for _ in range(rounds):
        winner = bot_vs_bot(bot1, bot2)
        results[winner] += 1
    return results

if __name__ == "__main__":
    print("SimpleBot vs RandomBot:", test_bots(simple_bot, random_bot))
    print("SimpleBot vs MinimaxBot:", test_bots(simple_bot, minimax_bot))
