import socket
import json
import sys
from random_bot import random_aibot
from simple_bot import simple_aibot
from minimax_bot import minimax_aibot
from utils import is_full  # 用于判断棋盘是否已满（避免极端场景）
from xuanzejiemianTest import XuanZeJieMian
from PySide2.QtWidgets import QApplication
# 通信协议配置（需与主控程序保持完全一致）
BUFFER_SIZE = 4096  # 数据缓冲区大小
ENCODING = "utf-8"  # 字符编码


# 协议指令格式：请求为"request_move"（主控发），响应为"response_move"（算法发）


def parse_request_data(data_str):
    """解析主控程序发来的请求数据，验证格式合法性
    输入参数：字符串形式的字典,格式要求示例：“{”type":"....","board":".....","player":"...."}
    返回值：元组格式，(board,player)
    抛出异常
    """
    try:
        data = json.loads(data_str)
        # 校验必要字段：请求类型、棋盘、当前玩家
        if (data.get("type") != "request_move"
                or "board" not in data
                or "player" not in data
                or data["player"] not in ["X", "O"]):
            raise ValueError("请求格式错误：缺少必要字段或字段值非法")
        return data["board"], data["player"]  # 返回算法需要的核心参数
    except json.JSONDecodeError:
        raise ValueError("请求数据不是合法JSON格式")
    except Exception as e:
        raise ValueError(f"解析请求失败：{str(e)}")


def call_bot_algorithm(board, player, bot_type="simple_bot", minimax_depth=3):
    """根据指定的bot类型，调用对应算法计算落子坐标
    输入参数：board(list), player(str), bot_type(str), minimax_dept(int)
    返回值：(row,col),落子坐标
    抛出异常
    """
    try:
        if is_full(board):
            raise Exception("棋盘已满，无需落子")

        # 调用对应算法
        if bot_type == "random_bot":
            return random_aibot(board, player)
        elif bot_type == "simple_bot":
            return simple_aibot(board, player)
        elif bot_type == "minimax_bot":
            return minimax_aibot(board, player, depth=minimax_depth)
        else:
            raise ValueError(f"不支持的bot类型：{bot_type}，可选值：random_bot/simple_bot/minimax_bot")
    except Exception as e:
        raise Exception(f"算法计算落子失败：{str(e)}")


def socket_client(host="127.0.0.1", port=12345, bot_type="simple_bot", minimax_depth=3):
    """
    Socket客户端主逻辑：连接主控、接收请求、调用算法、返回响应
    输入参数：
     host: 主控程序IP地址（默认本地）
     port: 主控程序Socket端口（默认12345）
     bot_type: 选择使用的算法（默认simple_bot）
     minimax_depth: minimax算法搜索深度（默认3，深度越大越智能但耗时更长）

    返回值：None
    异常抛出
    """
    client_socket = None
    try:
        # 1. 创建Socket并连接主控
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"✅ 已连接主控程序（{host}:{port}），使用算法：{bot_type}")

        # 2. 循环接收主控请求（一局游戏可能多次接收落子请求）
        while True:
            # 接收主控发送的请求数据
            request_data = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
            if not request_data:
                print("❌ 主控程序断开连接，退出客户端")
                break

            print(f"\n📥 收到主控请求：{request_data[:100]}...")  # 打印前100字符避免过长

            # 3. 解析请求并调用算法
            board, player = parse_request_data(request_data)
            row, col = call_bot_algorithm(board, player, bot_type, minimax_depth)

            # 4. 构造响应数据（JSON格式）
            response = {
                "type": "response_move",
                "row": row,
                "col": col,
                "status": "success"
            }
            response_str = json.dumps(response)
            print(f"📤 发送落子响应：{response_str}")

            # 5. 发送响应给主控
            client_socket.sendall(response_str.encode(ENCODING))

    except Exception as e:
        print(f"❌ 通信或算法错误：{str(e)}")
    finally:
        # 关闭Socket连接
        if client_socket:
            client_socket.close()
            print("🔌 已关闭Socket连接")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    xuanze = XuanZeJieMian()
    xuanze.ui.show()
    bot_type = xuanze.getBotType()
    app.exec_()
    # 示例：运行客户端（可通过命令行参数或直接修改参数）
    # 用法1：默认参数（本地主控+simple_bot）
    # socket_client()

    # 用法2：指定参数（例如：连接远程主控+minimax_bot，搜索深度4）
    socket_client(
        host="127.0.0.1",  # 替换为主控程序的IP
        port=12345,  # 替换为主控程序的Socket端口
        bot_type=bot_type,  # 选择算法：random_bot/simple_bot/minimax_bot
        minimax_depth=4  # 仅minimax_bot生效，建议3-5（过深会卡顿）
    )
