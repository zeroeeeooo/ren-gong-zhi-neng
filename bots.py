| 函数名                                              | 输入参数类型                   | 返回值类型             | 功能简述     |
| :----------------------------------------------- | :----------------------- | :---------------- | :------- |
| `create_board(size: int = 9)`                    | `int`                    | `list[list[str]]` | 创建空棋盘    |
| `check_win(board: list[list[str]], player: str)` | `list[list[str]]`, `str` | `bool`            | 判断是否连成五子 |
| `is_full(board: list[list[str]])`                | `list[list[str]]`        | `bool`            | 检查棋盘是否下满 |
| `switch_player(player: str)`                     | `str`                    | `str`             | 轮换玩家标记   |
