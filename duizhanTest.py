from PySide2.QtWidgets import QApplication,QMessageBox, QLabel, QGraphicsOpacityEffect
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile 
from PySide2 import QtCore
from PySide2.QtCore import QObject, QEvent
from PySide2.QtGui import QMouseEvent, QPixmap
from qizi import BaiQiZi, HeiQiZi, xstartplace, ystartplace, QiZilengthGap, QiZiheightGap, QiZilength, QiZiheight

class DuiZhanJieMian(QObject):
    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load("./src/ui/对战界面.ui")
        self.ui.setWindowTitle("五子棋")
        # 存放已创建的棋子对象，便于管理/隐藏/删除
        self.pieces = []
        # 棋盘大小：19 列 x 13 行（x 从 0..18，y 从 0..12）
        self.cols = 19
        self.rows = 13
        # 使用 0 表示空，1 表示白子，2 表示黑子
        self.grid = [[0 for _ in range(self.cols)] for __ in range(self.rows)]
        # 当前下子颜色（1 白, 2 黑），默认白子先手
        self.current_color = 1
        self.ui.backbtn.clicked.connect(self.back_clicked)


    def back_clicked(self):
        '''self.ui.close()
        self.zhujiemian = ZhuJieMian()
        self.zhujiemian.ui.show()
        '''
        self.reset_board()

    def show_piece(self, pos, color='white'):
        """
        在棋盘上显示一个棋子。
        pos: (x, y) 元组，表示棋盘格坐标（整数）
        color: 'white' 或 'black'（不区分大小写）
        返回创建的棋子对象。
        """
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            raise ValueError("pos 必须是 (x, y) 的元组或列表")

        x, y = pos
        color = str(color).lower()
        if color in ('white', 'w', 'bai', '白'):
            piece = BaiQiZi()
        else:
            piece = HeiQiZi()

        # 设置位置并将 QLabel 设为 qipan 的子控件以显示在棋盘上
        piece.setPosition(x, y)
        piece.label.setParent(self.ui.qipan)
        piece.label.show()
        piece.label.raise_()

        self.pieces.append(piece)
        return piece

    def is_inside(self, pos):
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            return False
        x, y = pos
        return 0 <= x < self.cols and 0 <= y < self.rows

    def is_empty(self, pos):
        if not self.is_inside(pos):
            return False
        x, y = pos
        return self.grid[y][x] == 0

    def place_piece(self, pos, color='white'):
        """
        在逻辑棋盘上放置棋子：先检查位置是否有效且为空，
        然后调用 show_piece 在界面上显示并更新状态。返回 True/False 表示是否成功放置。
        """
        if not self.is_inside(pos):
            return False
        if not self.is_empty(pos):
            return False

        piece = self.show_piece(pos, color)
        x, y = pos
        clr = str(color).lower()
        self.grid[y][x] = 1 if clr in ('white', 'w', 'bai', '白') else 2
        # 切换当前颜色
        self.current_color = 2 if self.current_color == 1 else 1
        return True

    def reset_board(self):
        # 隐藏并删除所有棋子对象，重置状态数组
        for p in self.pieces:
            try:
                p.label.hide()
                p.label.setParent(None)
                p.label.deleteLater()
            except Exception:
                pass
        self.pieces = []
        self.grid = [[0 for _ in range(self.cols)] for __ in range(self.rows)]
        # 隐藏 hover 并重置当前颜色
        try:
            if self.hover:
                self.hover.hide()
        except Exception:
            pass
        self.current_color = 1
        # 让 Qt 事件循环处理删除（确保 QLabel 被销毁/从界面移除）
        try:
            QtCore.QCoreApplication.processEvents()
        except Exception:
            pass

    def eventFilter(self, watched, event):
        # 仅处理 qipanimg 上的鼠标按下事件
        if watched is self.qipanimg:
            etype = event.type()
            # 获取局部坐标
            try:
                px = event.pos().x()
                py = event.pos().y()
            except Exception:
                return False

            # 获取 pixmap 与 label 大小，计算显示的 pixmap 显示区域（考虑保持纵横比）
            pm = self.qipanimg.pixmap()
            label_w = self.qipanimg.width()
            label_h = self.qipanimg.height()

            if pm is None:
                return False

            pm_w = pm.width()
            pm_h = pm.height()

            if self.qipanimg.hasScaledContents():
                disp_w = label_w
                disp_h = label_h
                offset_x = 0
                offset_y = 0
            else:
                # 保持纵横比缩放
                scale = min(label_w / pm_w, label_h / pm_h)
                disp_w = pm_w * scale
                disp_h = pm_h * scale
                offset_x = int((label_w - disp_w) / 2)
                offset_y = int((label_h - disp_h) / 2)

            # 如果在 label 内的点击不在 pixmap 显示区域则忽略 hover/点击
            if px < offset_x or px > offset_x + disp_w or py < offset_y or py > offset_y + disp_h:
                # 隐藏 hover（如果存在）
                if etype == QEvent.MouseMove and self.hover:
                    self.hover.hide()
                return False

            # 计算 qipan 坐标系中的点击点（相对于 qipan 的像素）
            img_offset_x = self.qipanimg.x()
            img_offset_y = self.qipanimg.y()
            # 实际点击在 pixmap 内的相对位置（相对于 pixmap 显示区域左上）
            px_in_disp = px - offset_x
            py_in_disp = py - offset_y
            # 转换为 qipan 坐标
            click_x_qipan = img_offset_x + offset_x + px_in_disp
            click_y_qipan = img_offset_y + offset_y + py_in_disp

            # 计算格坐标
            raw_x = (click_x_qipan - xstartplace) / QiZilengthGap
            raw_y = (click_y_qipan - ystartplace) / QiZiheightGap
            # 初始坐标往左平移一列：将计算结果左移一列以匹配视觉布局
            grid_x = int(round(raw_x)) - 1
            grid_y = int(round(raw_y))

            # 限定范围
            if not (0 <= grid_x < self.cols and 0 <= grid_y < self.rows):
                if etype == QEvent.MouseMove and self.hover:
                    self.hover.hide()
                return False

            # 处理移动事件：显示 hover
            if etype == QEvent.MouseMove and self.hover is not None:
                # 计算 hover 的像素位置（同 QiZi.setPosition）
                hx = grid_x * QiZilengthGap + xstartplace
                hy = grid_y * QiZiheightGap + ystartplace
                self.hover.move(hx, hy)
                # 根据是否该位置可下子，改变 hover 显示（可选：不同颜色或隐藏）
                if self.is_empty((grid_x, grid_y)):
                    # 显示当前颜色的半透明棋子
                    if self.current_color == 1:
                        try:
                            pm_preview = QPixmap("./src/picture/白子.jpg")
                            self.hover.setPixmap(pm_preview)
                            self.hover.setScaledContents(True)
                        except Exception:
                            pass
                    else:
                        try:
                            pm_preview = QPixmap("./src/picture/黑子.jpg")
                            self.hover.setPixmap(pm_preview)
                            self.hover.setScaledContents(True)
                        except Exception:
                            pass
                    self.hover.show()
                else:
                    self.hover.hide()
                return True

            # 处理鼠标按下事件：实际下子
            if etype == QEvent.MouseButtonPress:
                color = 'white' if self.current_color == 1 else 'black'
                placed = self.place_piece((grid_x, grid_y), color)
                if placed:
                    # 隐藏 hover 并返回
                    if self.hover:
                        self.hover.hide()
                return True

        return super(DuiZhanJieMian, self).eventFilter(watched, event)


