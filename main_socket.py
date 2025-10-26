import socket
import json
from utils import create_board, check_win, is_full, switch_player  # 复用之前的工具函数

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
    finally:
        # 关闭连接（无论是否出错，都要释放资源）
        if "client_conn" in locals():
            client_conn.close()
            print("已关闭与客户端的连接")
        server_socket.close()
        print("已关闭主控服务端")

if __name__ == "__main__":
    main()
