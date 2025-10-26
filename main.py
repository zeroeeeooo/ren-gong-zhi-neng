from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QTimer
from qizi import QiZi, BaiQiZi, HeiQiZi
from zhujiemianTest import ZhuJieMian
from duizhanTest import DuiZhanJieMian
import sys
import time
from utils import create_board, check_win, is_full, switch_player
from random_bot import random_bot
from minimax_bot import minimax_bot
from simple_bot import simple_bot

def StartZhuJieMian(zhujiemian):
    zhujiemian.ui.show()

def CloseZhuJieMian(zhujiemian):
    zhujiemian.ui.close()

def StartDuiZhanJieMian(duizhanjiemian):
    duizhanjiemian.ui.show()

def CloseDuiZhanJieMian(duizhanjiemian):
    duizhanjiemian.ui.close()

def xiaqitest(qizi, qipan, x, y):
    qizi.setPosition(x, y)
    qizi.label.setParent(qipan)
    qizi.label.show()
    qizi.label.raise_()

def yincangqizi(qizi):
    qizi.label.setVisible(False)

def xianshishiqizi(qizi):
    qizi.label.setVisible(True)


def run_gui_match(bot_X, bot_X_name, bot_O, bot_O_name, view=None, board_size=13, depth_X=None, depth_O=None, first_player='X', delay=0.5):
    """
    在 GUI 中让两个 bot 对战并可视化落子。

    参数:
      bot_X, bot_O: 两个 bot 函数，签名通常为 (board, player) 或 (board, player, depth)
      board_size: 棋盘大小 (默认 9)
      depth_X, depth_O: 如果 bot 支持 depth 参数，可传入对应深度（否则传 None）
      first_player: 'X' 或 'O'，谁先手
      delay: 每步之间的时间间隔（秒）

    Bot 函数约定：接受 (board, player) 或 (board, player, depth=...)，返回 (row, col)
    """


    current_player = first_player
    bots = {"X": bot_X, "O": bot_O}

    # 创建棋盘和视图（如果外部没有传入 view）
    board = create_board(board_size)
    if view is None:
        view = DuiZhanJieMian()
        view.ui.show()

    results = {"X": 0, "O": 0, "draw": 0}
    last_winner = None

    def call_bot(bot, board, player, depth):
        try:
            if depth is None:
                return bot(board, player)
            else:
                return bot(board, player, depth=depth)
        except TypeError:
            # bot 可能不接受 depth 参数
            return bot(board, player)

    def make_move():
        nonlocal current_player
        bot = bots[current_player]
        depth = depth_X if current_player == 'X' else depth_O
        move = call_bot(bot, board, current_player, depth)

        if not isinstance(move, (tuple, list)) or len(move) != 2:
            print(f"Bot {current_player} 返回非法 move: {move}")
            finished_flag['done'] = True
            last_winner = 'draw'
            return

        r, c = move
        # 检查并执行
        if board[r][c] != ".":
            print(f"Bot {current_player} 试图落子到已占位置 {(r,c)}，终止对局")
            # 视为对方胜
            winner = 'O' if current_player == 'X' else 'X'
            results[winner] += 1
            last_winner = winner
            finished_flag['done'] = True
            return

        board[r][c] = current_player
        # 在 GUI 棋盘上显示（board 是 row/col, UI 接受 (x=col, y=row)）
        view.place_piece((c, r), 'white' if current_player == 'X' else 'black')

        if check_win(board, current_player):
            if current_player == 'X':
                win_player = bot_X_name
            else:
                win_player = bot_O_name
            QMessageBox.information(view.ui, "游戏结束", f"游戏结束，获胜者: {win_player}")
            results[current_player] += 1
            last_winner = current_player
            finished_flag['done'] = True
            return
        if is_full(board):
            results['draw'] += 1
            last_winner = 'draw'
            finished_flag['done'] = True
            return

        # 切换当前玩家
        current_player = switch_player(current_player)

    # 使用定时器在 GUI 事件循环中逐步下子
    timer = QTimer()
    timer.setInterval(int(delay * 1000))

    finished_flag = {'done': False}

    def on_timeout():
        if not finished_flag['done']:
            make_move()
        else:
            timer.stop()

    timer.timeout.connect(on_timeout)
    timer.start()

    # 阻塞直到本局结束（在事件循环中处理事件）
    from time import sleep
    while not finished_flag['done']:
        QApplication.processEvents()
        sleep(0.01)

    # 局结束后确保界面刷新并返回
    QApplication.processEvents()

    return current_player





if __name__ == '__main__':
    app = QApplication([])

    # 示例：在同一个 GUI 上运行一场 Random vs Minimax 的对战
    view = DuiZhanJieMian()
    view.ui.show()

    bots = [random_bot, simple_bot, minimax_bot]

    # 机器人编号映射：random_bot -> 1, simple_bot -> 2, minimax_bot -> 3
    bot_number = {random_bot.__name__: 1, simple_bot.__name__: 2, minimax_bot.__name__: 3}
    # 初始化统计
    robot_stats = {
        1: {'wins': 0, 'losses': 0},
        2: {'wins': 0, 'losses': 0},
        3: {'wins': 0, 'losses': 0},
    }

    def refresh_robot_labels():
        # 更新顶部三个机器人 QLabel 文本
        try:
            view.ui.robot1.setText(f"机器人1   胜场:{robot_stats[1]['wins']}   败场:{robot_stats[1]['losses']}")
            view.ui.robot2.setText(f"机器人2   胜场:{robot_stats[2]['wins']}   败场:{robot_stats[2]['losses']}")
            view.ui.robot3.setText(f"机器人3   胜场:{robot_stats[3]['wins']}   败场:{robot_stats[3]['losses']}")
        except Exception:
            pass

    # 初始化顶部统计显示
    refresh_robot_labels()

    # 顺序进行每对 bots 的对战，每场等待结束后再开始下一场（先手为 X 在左侧）
    for bot1 in bots:
        for bot2 in bots:
            if bot2 == bot1:
                continue
            # 设置左右侧显示为：左侧为先手（X），右侧为后手（O）
            num1 = bot_number.get(bot1.__name__, 0)
            num2 = bot_number.get(bot2.__name__, 0)
            # 开始每场对战前先清空棋盘
            try:
                view.reset_board()
                QApplication.processEvents()
                time.sleep(0.05)
            except Exception:
                pass
            try:
                view.ui.robotText1.setText(f"机器人{num1} (先手)")
                view.ui.robotText2.setText(f"机器人{num2} (后手)")
            except Exception:
                print("Error updating robot text labels")

            print(f"Starting match: {bot1.__name__} (X) vs {bot2.__name__} (O)")
            winner = run_gui_match(bot1, bot1.__name__, bot2, bot2.__name__, view=view, board_size=13, depth_X=None, depth_O=2, first_player='X', delay=0.6)
            print(f"Match ended. Winner: {winner}")
            # 更新统计
            if winner == 'X':
                # X 为左侧 bot1 胜
                robot_stats[num1]['wins'] += 1
                robot_stats[num2]['losses'] += 1
            elif winner == 'O':
                robot_stats[num2]['wins'] += 1
                robot_stats[num1]['losses'] += 1
            else:
                # draw: 不更新胜负，仅刷新标签
                pass

            # 刷新统计显示并清空棋盘为下一场准备
            refresh_robot_labels()
            try:
                view.reset_board()
                print(robot_stats[num1]['wins'])
                QApplication.processEvents()
                time.sleep(0.05)
            except Exception:
                pass


    sys.exit(app.exec_())

