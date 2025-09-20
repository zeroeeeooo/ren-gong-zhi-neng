# Gomoku Bots 🤖

本项目实现了几个五子棋 AI 机器人，用于研究不同算法的效果。

## 机器人类型
- **RandomBot**: 随机落子
- **SimpleBot**: 简单启发式（赢棋优先 → 堵棋 → 随机）
- **MinimaxBot**: 启发式评分 + Minimax 搜索 + Alpha-Beta 剪枝

## 运行测试
```bash
python tests/test_bots.py

