import numpy as np
import random
from collections import defaultdict


class GobangAI:
    def __init__(self, board_size=15, win_condition=5):
        """
        说明：初始化五子棋AI
        参数:board_size: 棋盘大小，默认为15x15
            win_condition: 获胜所需的连续棋子数，默认为5
        返回：无
        """
        self.board_size = board_size
        self.win_condition = win_condition
        self.board = np.zeros((board_size, board_size), dtype=int)  # 0: 空, 1: 己方, 2: 对方
        self.current_player = 1  # 1: 己方, 2: 对方
        self.directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 水平、垂直、对角线、反对角线

        # 不同棋型的评分
        self.score_patterns = {
            'five': 100000,  # 五连
            'open_four': 10000,  # 活四
            'four': 1000,  # 冲四
            'open_three': 1000,  # 活三
            'three': 100,  # 眠三
            'open_two': 100,  # 活二
            'two': 10,  # 眠二
            'one': 1  # 单子
        }

    def reset(self):
        """
        说明：重置棋盘和游戏状态
        参数：无
        返回：无
        """
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1

    def set_board(self, board_state):
        """
        说明：设置棋盘状态
        参数:board_state: 二维数组，表示棋盘状态，0: 空, 1: 己方, 2: 对方
        返回：无
        """
        self.board = np.array(board_state)

    def is_valid_move(self, x, y):
        """
        说明：检查移动是否有效
        参数：X，Y坐标（int）
        返回：bool
        """
        return 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == 0

    def make_move(self, x, y):
        """
        说明：在指定位置落子
        参数：X，Y
        返回：bool
        """
        if self.is_valid_move(x, y):
            self.board[x][y] = self.current_player
            self.current_player = 3 - self.current_player  # 切换玩家 (1->2, 2->1)
            return True
        return False

    def undo_move(self, x, y):
        """
        说明：撤销落子
        参数：X，Y
        返回：bool
        """
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            self.board[x][y] = 0
            self.current_player = 3 - self.current_player  # 切换回原玩家
            return True
        return False

    def get_valid_moves(self):
        """
        说明：获取所有有效的可落子位置
        参数：无
        返回：列表:valid_moves (list[tuple(int,int)])
        """
        valid_moves = []

        # 优化：只考虑已有棋子周围的空位
        if np.count_nonzero(self.board) > 0:
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.board[i][j] == 0 and self.has_neighbor(i, j):
                        valid_moves.append((i, j))
        else:
            # 如果棋盘为空，只考虑中心区域
            center = self.board_size // 2
            for i in range(max(0, center - 2), min(self.board_size, center + 3)):
                for j in range(max(0, center - 2), min(self.board_size, center + 3)):
                    valid_moves.append((i, j))

        return valid_moves if valid_moves else [(self.board_size // 2, self.board_size // 2)]

    def has_neighbor(self, x, y, distance=2):
        """
        说明：检查指定位置周围是否有棋子
        参数：X，Y，distance(默认为2，表示检查周围两格范围)
        返回：bool
        """
        for i in range(max(0, x - distance), min(self.board_size, x + distance + 1)):
            for j in range(max(0, y - distance), min(self.board_size, y + distance + 1)):
                if self.board[i][j] != 0:
                    return True
        return False

    def check_win(self, x, y):
        """
        说明：检查是否获胜
        参数：X，Y
        返回：bool
        """
        player = self.board[x][y]
        if player == 0:
            return False

        for dx, dy in self.directions:
            count = 1  # 当前位置已经有一个棋子

            # 正向检查
            temp_x, temp_y = x + dx, y + dy
            while 0 <= temp_x < self.board_size and 0 <= temp_y < self.board_size and self.board[temp_x][
                temp_y] == player:
                count += 1
                temp_x += dx
                temp_y += dy

            # 反向检查
            temp_x, temp_y = x - dx, y - dy
            while 0 <= temp_x < self.board_size and 0 <= temp_y < self.board_size and self.board[temp_x][
                temp_y] == player:
                count += 1
                temp_x -= dx
                temp_y -= dy

            if count >= self.win_condition:
                return True

        return False

    def evaluate_position(self, x, y, player):
        """
        说明：临时落子以评估某个位置的价值
        参数：X，Y，player(玩家编号）
        返回：score(int，该位置对指定玩家的评估分数)
        """
        if not self.is_valid_move(x, y):
            return -1

        # 临时落子以评估
        self.board[x][y] = player
        score = self._evaluate_board(player)
        self.board[x][y] = 0  # 恢复

        return score

    def _evaluate_board(self, player):
        """
        说明：评估整个棋盘对指定玩家的价值
        参数：player(玩家编号)
        返回：score(当前棋盘状态对指定玩家的总评分)
        """
        score = 0
        opponent = 3 - player    #对手

        # 检查所有方向的棋型
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == player:
                    # 己方棋子
                    for dx, dy in self.directions:
                        pattern = self._get_pattern(i, j, dx, dy, player)
                        score += self._get_pattern_score(pattern)
                elif self.board[i][j] == opponent:
                    # 对方棋子（防守价值）
                    for dx, dy in self.directions:
                        pattern = self._get_pattern(i, j, dx, dy, opponent)
                        score -= self._get_pattern_score(pattern) * 0.8  # 防守权重略低

        return score

    def _get_pattern(self, x, y, dx, dy, player):
        """
        说明：获取从(x,y)开始在(dx,dy)方向上的棋型
        参数：X，Y，dx,dy,player
        返回：patter(list[])"""
        pattern = []
        for i in range(self.win_condition + 2):  # 多检查几个位置以确保完整棋型
            nx, ny = x + i * dx, y + i * dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if self.board[nx][ny] == player:
                    pattern.append(1)  # 己方棋子
                elif self.board[nx][ny] == 0:
                    pattern.append(0)  # 空位
                else:
                    pattern.append(2)  # 对方棋子
            else:
                pattern.append(2)  # 超出边界视为对方棋子

        return pattern

    def _get_pattern_score(self, pattern):
        """
        说明：根据棋型返回分数
        参数：pattern(list)
        返回：分数，int
        """
        pattern_str = ''.join(map(str, pattern))

        # 五连
        if '11111' in pattern_str:
            return self.score_patterns['five']

        # 活四
        if '011110' in pattern_str:
            return self.score_patterns['open_four']

        # 冲四
        if any(p in pattern_str for p in ['011112', '211110', '0111010', '0101110']):
            return self.score_patterns['four']

        # 活三
        if any(p in pattern_str for p in ['01110', '010110', '011010']):
            return self.score_patterns['open_three']

        # 眠三
        if any(p in pattern_str for p in ['001112', '211100', '010112', '211010', '00110', '01100']):
            return self.score_patterns['three']

        # 活二
        if any(p in pattern_str for p in ['00110', '01100', '01010', '010010']):
            return self.score_patterns['open_two']

        # 眠二
        if any(p in pattern_str for p in ['00112', '21100', '10001', '00101', '10100']):
            return self.score_patterns['two']

        # 单子
        if '1' in pattern_str:
            return self.score_patterns['one']

        return 0

    def minimax(self, depth, alpha, beta, maximizing_player):
        """
        说明：极小化极大算法，带Alpha-Beta剪枝
        参数：depth(搜索深度，int），alpha（当前玩家最优下限,float），beta（对手最优上限,float），maximizing_player(bool)
        返回：（min_eval/max_eval, best_move）评估分数，最佳落子位置"""
        # 检查终止条件
        if depth == 0:
            return self._evaluate_board(1), None

        valid_moves = self.get_valid_moves()

        if maximizing_player:
            max_eval = float('-inf')
            best_move = None

            for x, y in valid_moves:
                if self.make_move(x, y):
                    # 检查是否获胜
                    if self.check_win(x, y):
                        self.undo_move(x, y)
                        return self.score_patterns['five'], (x, y)

                    eval_score, _ = self.minimax(depth - 1, alpha, beta, False)
                    self.undo_move(x, y)

                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_move = (x, y)

                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break  # Beta剪枝

            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None

            for x, y in valid_moves:
                if self.make_move(x, y):
                    # 检查是否获胜
                    if self.check_win(x, y):
                        self.undo_move(x, y)
                        return -self.score_patterns['five'], (x, y)

                    eval_score, _ = self.minimax(depth - 1, alpha, beta, True)
                    self.undo_move(x, y)

                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = (x, y)

                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break  # Alpha剪枝

            return min_eval, best_move

    def get_best_move(self, depth=5):
        """
        说明：获取最佳落子位置
        参数：depth
        返回：最佳落子坐标，tuple"""
        best_move = self.minimax(depth, float('-inf'), float('inf'), True)
        return best_move

    def get_random_move(self):
        """
        说明：获取随机落子位置（用于简单测试）
        参数：无
        返回：随机坐标"""
        valid_moves = self.get_valid_moves()
        return random.choice(valid_moves) if valid_moves else None