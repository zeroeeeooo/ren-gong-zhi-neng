import sys
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtCore import QTimer
from utils import create_board, check_win, is_full, switch_player
from random_bot import random_bot
from minimax_bot import minimax_bot
from duizhanTest import DuiZhanJieMian


def run_gui_match(bot_X, bot_O, rounds=5, board_size=9, depth_X=None, depth_O=2, first_player='X', delay=600):
    """
    在 GUI 中按局进行对战：每局结束后弹窗提示结果，用户确认后进入下一局。
    bot_X / bot_O: 函数，签名如 random_bot(board, player) 或 minimax_bot(board, player, depth=...)
    rounds: 要进行的总局数
    board_size: 棋盘大小（方阵）
    depth_X / depth_O: 当 bot 是 minimax 时传入的深度（或 None）
    delay: 每步之间的毫秒延迟
    """
    app = QApplication([])
    view = DuiZhanJieMian()
    view.ui.show()

    results = {"X": 0, "O": 0, "draw": 0}
    current_round = {"i": 0}

    def play_one_round():
        # 初始化一局
        board = create_board(board_size)
        view.reset_board()
        # Ensure UI has processed deletions and is cleared before starting moves
        app.processEvents()
        # small delay to let Qt finish widget cleanup
        from time import sleep
        sleep(0.05)
        current_player = first_player
        finished_flag = {"done": False}

        timer = QTimer()
        timer.setInterval(delay)

        def make_move():
            nonlocal current_player
            if finished_flag["done"]:
                return

            bot = bot_X if current_player == 'X' else bot_O
            # 适配不同 bot 的签名
            if bot == minimax_bot:
                depth = depth_X if current_player == 'X' else depth_O
                move = bot(board, current_player, depth=depth)
            else:
                move = bot(board, current_player)

            if move is None:
                # 如果 bot 没有返回合法落子，视为平局
                timer.stop()
                finished_flag["done"] = True
                results["draw"] += 1
                return

            r, c = move
            # 保护性判断
            if board[r][c] != ".":
                # 非法动作，视为对方胜
                winner = 'O' if current_player == 'X' else 'X'
                timer.stop()
                finished_flag["done"] = True
                results[winner] += 1
                return

            board[r][c] = current_player
            # 在 GUI 上显示（board 使用 row/col，界面使用 x=col,y=row）
            view.place_piece((c, r), 'white' if current_player == 'X' else 'black')

            # 检查是否胜利或平局
            if check_win(board, current_player):
                timer.stop()
                finished_flag["done"] = True
                results[current_player] += 1
                return
            if is_full(board):
                timer.stop()
                finished_flag["done"] = True
                results["draw"] += 1
                return

            # 切换玩家
            current_player = switch_player(current_player)

        timer.timeout.connect(make_move)
        timer.start()

        # 等待本局结束（通过事件循环和定时器驱动），当结束时弹窗并询问是否继续
        while not finished_flag["done"]:
            app.processEvents()

        # 弹窗显示结果
        current_round["i"] += 1
        msg = f"第 {current_round['i']} 局 结果： X={results['X']}  O={results['O']}  draw={results['draw']}"

        box = QMessageBox()
        box.setWindowTitle("一局结束")
        box.setText(msg)
        box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = box.exec_()
        return ret == QMessageBox.Ok

    # 主循环：逐局进行
    for _ in range(rounds):
        cont = play_one_round()
        if not cont:
            break

    # 显示最终统计
    final_box = QMessageBox()
    final_box.setWindowTitle("对战结束")
    final_box.setText(f"最终结果：X={results['X']}  O={results['O']}  draw={results['draw']}")
    final_box.exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    # 示例：随机 bot (X) 对 minimax bot (O)，共 3 局
    run_gui_match(random_bot, minimax_bot, rounds=3, board_size=9, depth_X=None, depth_O=2, first_player='X', delay=400)
