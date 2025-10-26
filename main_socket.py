'''
import socket
import json
from utils import create_board, check_win, is_full, switch_player  # 复用之前的工具函数
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QTimer
from qizi import QiZi, BaiQiZi, HeiQiZi
from zhujiemianTest import ZhuJieMian
from duizhanTest import DuiZhanJieMian
import sys
import time
# -------------------------- 1. 服务端配置（需与客户端一致） --------------------------
HOST = "127.0.0.1"  # 服务端IP（本地测试用127.0.0.1，局域网用本机IP）
PORT = 12345         # 端口号：必须与算法客户端的port完全一致
BUFFER_SIZE = 4096   # 数据缓冲区：与客户端保持一致
ENCODING = "utf-8"   # 编码格式：与客户端保持一致，避免乱码

# -------------------------- 2. 主控核心逻辑（匹配+对战） --------------------------



def main():
    # 1. 创建Socket服务端对象（TCP协议）
    # socket.AF_INET：互联网协议；socket.SOCK_STREAM：TCP可靠传输
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定IP和端口（让客户端知道“连哪里”）
    server_socket.bind((HOST, PORT))
    # 开始监听：允许1个客户端同时连接（循环赛可扩展为多客户端队列）
    server_socket.listen(1)
    print(f"主控服务端已启动，正在{HOST}:{PORT}等待算法客户端连接...")

    try:
        # 2. 等待并接受客户端连接（阻塞态，直到有客户端连进来）
        client_conn, client_addr = server_socket.accept()
        print(f"已与算法客户端{client_addr}建立连接，开始对战！")

        # 3. 初始化游戏数据
        board = create_board(size=9)  # 创建9x9空棋盘
        current_player = "X"          # 先手玩家（可自定义）
        game_over = False             # 游戏是否结束

        # 4. 游戏主循环（每一轮：发请求→收响应→判胜负）
        while not game_over:
            print(f"\n===== 当前回合：玩家{current_player} 落子 =====")
            # 打印当前棋盘（可视化，方便查看）
            for row in board:
                print(" ".join(row))

            # -------------------------- 4.1 向客户端发送“落子请求” --------------------------
            # 构造请求数据（严格遵循与客户端约定的JSON协议）
            request_data = {
                "type": "request_move",  # 固定指令类型，客户端会解析
                "board": board,          # 当前完整棋盘状态
                "player": current_player # 本轮需要落子的玩家
            }
            # 把Python字典转成JSON字符串→再转成二进制（Socket只能传二进制）
            request_str = json.dumps(request_data).encode(ENCODING)
            # 发送请求给客户端
            client_conn.sendall(request_str)
            print(f"📤 已向客户端发送落子请求（玩家{current_player}）")

            # -------------------------- 4.2 接收客户端的“落子响应” --------------------------
            # 接收客户端返回的二进制数据→转成JSON字符串→再转成Python字典
            response_bytes = client_conn.recv(BUFFER_SIZE)
            if not response_bytes:  # 客户端断开连接
                print("❌ 算法客户端主动断开连接，游戏结束")
                break
            response_str = response_bytes.decode(ENCODING)
            response_data = json.loads(response_str)
            print(f"📥 收到客户端落子响应：行{response_data['row']}，列{response_data['col']}")

            # -------------------------- 4.3 执行落子+裁判判罚 --------------------------
            # 从响应中提取落子坐标
            row = response_data["row"]
            col = response_data["col"]
            # 执行落子（更新棋盘，需确保坐标合法，此处简化处理）
            if board[row][col] == ".":  # 确认是空位
                board[row][col] = current_player
            else:
                print(f"❌ 客户端落子{row},{col}非法（已被占用），游戏结束")
                break

            # 调用裁判函数判胜负/平局
            if check_win(board, current_player):
                print(f"\n玩家{current_player}获胜！")
                game_over = True
            elif is_full(board):
                print(f"\n棋盘已满，平局！")
                game_over = True
            else:
                # 切换玩家，进入下一轮
                current_player = switch_player(current_player)

    except Exception as e:
        print(f"主控程序出错：{str(e)}")
'''
import socket
import json
import threading
import time
from utils import create_board, check_win, is_full, switch_player  # 复用之前的工具函数
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QTimer, QObject, Signal
from qizi import QiZi, BaiQiZi, HeiQiZi
from zhujiemianTest import ZhuJieMian
from duizhanTest import DuiZhanJieMian
import sys

# -------------------------- 1. 服务端配置（需与客户端一致） --------------------------
HOST = "127.0.0.1"  # 服务端IP（本地测试用127.0.0.1，局域网用本机IP）
PORT = 12345         # 端口号：必须与算法客户端的port完全一致
BUFFER_SIZE = 4096   # 数据缓冲区：与客户端保持一致
ENCODING = "utf-8"   # 编码格式：与客户端保持一致，避免乱码


class SocketWorker(QObject):
    """后台 socket 工作线程：接收客户端落子并通过信号发送给 GUI 主线程来显示棋子。"""
    move_received = Signal(int, int, str)  # row, col, color_str ('white'/'black')
    info = Signal(str)

    def __init__(self, host=HOST, port=PORT, buffer_size=BUFFER_SIZE, encoding=ENCODING, board_size=19):
        super().__init__()
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.encoding = encoding
        self.board_size = board_size
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        """在独立线程中运行 socket 服务端。收到落子时 emit move_received(row, col, color)
        该方法会阻塞直到连接关闭或 stop() 被调用。"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)
        self.info.emit(f"主控服务端已启动，正在{self.host}:{self.port}等待算法客户端连接...")

        try:
            client_conn, client_addr = server_socket.accept()
            self.info.emit(f"已与算法客户端{client_addr}建立连接，开始对战！")

            board = create_board(size=self.board_size)
            current_player = "X"
            game_over = False

            while not game_over and not self._stop.is_set():
                # 发送请求给客户端，要求其返回下一步（原始协议保留）
                request_data = {"type": "request_move", "board": board, "player": current_player}
                try:
                    client_conn.sendall(json.dumps(request_data).encode(self.encoding))
                except Exception as e:
                    self.info.emit(f"发送请求失败：{e}")
                    break

                # 接收响应
                try:
                    response_bytes = client_conn.recv(self.buffer_size)
                except Exception as e:
                    self.info.emit(f"接收响应失败：{e}")
                    break

                if not response_bytes:
                    self.info.emit("客户端断开连接，结束对战")
                    break

                try:
                    response = json.loads(response_bytes.decode(self.encoding))
                except Exception as e:
                    self.info.emit(f"解析客户端响应失败：{e}")
                    break

                row = response.get('row')
                col = response.get('col')
                self.info.emit(f"收到客户端落子响应：行{row}，列{col}")

                # 简单合法性检查
                if row is None or col is None:
                    self.info.emit("收到无效坐标，终止对局")
                    break
                if not (0 <= row < self.board_size and 0 <= col < self.board_size):
                    self.info.emit("坐标超出范围，终止对局")
                    break

                if board[row][col] != '.':
                    self.info.emit(f"客户端落子{row},{col}已被占用，终止对局")
                    break

                # 更新逻辑棋盘并通过信号通知 GUI 放子（GUI 接受 (x=col, y=row)）
                board[row][col] = current_player
                color = 'white' if current_player == 'X' else 'black'
                # emit 信号（此信号是线程安全的，会在主线程执行槽）
                self.move_received.emit(row, col, color)

                # 判胜负
                if check_win(board, current_player):
                    self.info.emit(f"玩家{current_player}获胜！")
                    game_over = True
                elif is_full(board):
                    self.info.emit("棋盘已满，平局！")
                    game_over = True
                else:
                    current_player = switch_player(current_player)

            # 关闭连接
            try:
                client_conn.close()
            except Exception:
                pass

        except Exception as e:
            self.info.emit(f"主控程序出错：{e}")
        finally:
            try:
                server_socket.close()
            except Exception:
                pass
            self.info.emit("主控服务端已停止")


def start_gui_with_socket():
    app = QApplication([])
    view = DuiZhanJieMian()
    view.ui.show()

    worker = SocketWorker(board_size=19)

    # 将 worker 的 move_received 信号连接到 view.place_piece
    # 注意：view.place_piece 接受 pos=(x,y) 与 color 字符串
    def on_move(row, col, color):
        try:
            # 注意 view.place_piece 接收的是 (x=col, y=row)
            view.place_piece((col, row), color)
        except Exception as e:
            print(f"在 GUI 中放子失败：{e}")

    worker.move_received.connect(on_move)

    # 将信息信号打印到控制台（也可扩展到 UI 上）
    worker.info.connect(lambda s: print(s))

    # 在后台线程运行 socket 服务
    t = threading.Thread(target=worker.run, daemon=True)
    t.start()

    # 启动 Qt 事件循环
    sys.exit(app.exec_())


if __name__ == '__main__':
    start_gui_with_socket()