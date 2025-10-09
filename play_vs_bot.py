from game import create_board, print_board, check_win, is_full
from bots import minimax_bot

def play_vs_bot(board_size=15, bot_depth=3):
    board = create_board(board_size)
    human = "X"
    bot = "O"
    current_player = "X"

    print("欢迎来到五子棋！你是 X，AI 是 O。输入坐标格式：行 列 (例如: 7 7)\n")
    print_board(board)

    while True:
        if current_player == human:
            try:
                r, c = map(int, input("请输入你的落子坐标 (行 列): ").split())
                if board[r][c] != ".":
                    print("该位置已被占用，请重新输入！")
                    continue
                move = (r, c)
            except Exception:
                print("输入无效，请输入两个整数，例如: 7 7")
                continue
        else:
            print("AI 正在思考...")
            move = minimax_bot(board, bot, depth=bot_depth)
            print(f"AI 落子: {move}")

        board[move[0]][move[1]] = current_player
        print_board(board)
        print()

        if check_win(board, current_player):
            winner = "你" if current_player == human else "AI"
            print(f"游戏结束！{winner} 获胜！")
            break
        if is_full(board):
            print("游戏结束！平局！")
            break

        current_player = bot if current_player == human else human

if __name__ == "__main__":
    play_vs_bot(board_size=15, bot_depth=3)
