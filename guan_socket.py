import socket
import json
import threading
import time
from guantest import GobangAI


class GobangSocketInterface:
    def __init__(self, host='localhost', port=12345, ai_mode='minimax', ai_depth=5):
        """
        初始化五子棋Socket接口

        参数:
            host: 服务器地址
            port: 服务器端口
            ai_mode: AI模式，'minimax' 或 'random'
            ai_depth: AI搜索深度（仅对minimax模式有效）
        """
        self.host = host
        self.port = port
        self.ai_mode = ai_mode
        self.ai_depth = ai_depth
        self.ai = GobangAI()
        self.socket = None
        self.connected = False
        self.game_id = None
        self.player_id = None
        self.current_turn = None

        # 消息类型常量
        self.MSG_TYPE_CONNECT = "connect"
        self.MSG_TYPE_GAME_START = "game_start"
        self.MSG_TYPE_MOVE = "move"
        self.MSG_TYPE_OPPONENT_MOVE = "opponent_move"
        self.MSG_TYPE_GAME_OVER = "game_over"
        self.MSG_TYPE_DISCONNECT = "disconnect"
        self.MSG_TYPE_ERROR = "error"

    def connect_to_server(self):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True

            # 发送连接请求
            connect_msg = {
                "type": self.MSG_TYPE_CONNECT,
                "timestamp": time.time()
            }
            self.send_message(connect_msg)

            # 启动接收线程
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            print(f"已连接到服务器 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"连接服务器失败: {e}")
            return False

    def disconnect(self):
        """断开与服务器的连接"""
        if self.connected:
            # 发送断开连接消息
            disconnect_msg = {
                "type": self.MSG_TYPE_DISCONNECT,
                "game_id": self.game_id,
                "player_id": self.player_id,
                "timestamp": time.time()
            }
            self.send_message(disconnect_msg)

            self.socket.close()
            self.connected = False
            print("已断开与服务器的连接")

    def send_message(self, message):
        """发送消息到服务器"""
        if self.connected:
            try:
                # 将消息转换为JSON字符串并发送
                json_message = json.dumps(message)
                self.socket.sendall(json_message.encode('utf-8'))
                print(f"发送消息: {json_message}")
                return True
            except Exception as e:
                print(f"发送消息失败: {e}")
                return False
        return False

    def receive_messages(self):
        """接收服务器消息的线程函数"""
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data
                # 处理可能的多个JSON消息
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        try:
                            message = json.loads(line)
                            self.process_message(message)
                        except json.JSONDecodeError:
                            print(f"无效的JSON消息: {line}")
            except Exception as e:
                print(f"接收消息时出错: {e}")
                break

        self.connected = False

    def process_message(self, message):
        """处理接收到的消息"""
        msg_type = message.get("type")
        print(f"收到消息: {message}")

        if msg_type == self.MSG_TYPE_GAME_START:
            # 游戏开始
            self.game_id = message.get("game_id")
            self.player_id = message.get("player_id")
            self.current_turn = message.get("current_turn")
            board_state = message.get("board_state")

            # 设置AI棋盘状态
            self.ai.set_board(board_state)

            print(f"游戏开始! 游戏ID: {self.game_id}, 玩家ID: {self.player_id}")

            # 如果是己方回合，则下棋
            if self.current_turn == self.player_id:
                self.make_ai_move()

        elif msg_type == self.MSG_TYPE_OPPONENT_MOVE:
            # 对手落子
            opponent_move = message.get("move")
            board_state = message.get("board_state")
            self.current_turn = message.get("current_turn")

            # 更新AI棋盘状态
            self.ai.set_board(board_state)

            print(f"对手落子: {opponent_move}")

            # 如果是己方回合，则下棋
            if self.current_turn == self.player_id:
                self.make_ai_move()

        elif msg_type == self.MSG_TYPE_GAME_OVER:
            # 游戏结束
            winner = message.get("winner")
            reason = message.get("reason")

            print(f"游戏结束! 获胜者: {winner}, 原因: {reason}")

            # 可以选择断开连接或等待新游戏
            # self.disconnect()

        elif msg_type == self.MSG_TYPE_ERROR:
            # 错误消息
            error_msg = message.get("message")
            print(f"服务器错误: {error_msg}")

    def make_ai_move(self):
        """AI下棋"""
        if self.ai_mode == 'minimax':
            move = self.ai.get_best_move(depth=self.ai_depth)
        else:  # random
            move = self.ai.get_random_move()

        if move:
            x, y = move
            print(f"AI落子: ({x}, {y})")

            # 发送落子消息
            move_msg = {
                "type": self.MSG_TYPE_MOVE,
                "game_id": self.game_id,
                "player_id": self.player_id,
                "move": {"x": x, "y": y},
                "timestamp": time.time()
            }
            self.send_message(move_msg)
        else:
            print("无法找到有效的落子位置")

    def run(self):
        """运行Socket接口"""
        if self.connect_to_server():
            try:
                # 保持主线程运行
                while self.connected:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("用户中断，正在断开连接...")
            finally:
                self.disconnect()


if __name__ == "__main__":
    # 示例用法
    interface = GobangSocketInterface(host='localhost', port=12345, ai_mode='minimax', ai_depth=3)
    interface.run()