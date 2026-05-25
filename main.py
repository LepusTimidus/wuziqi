import tkinter as tk
from chessboard import BoardUI

# 创建主窗口
root = tk.Tk()
root.title("五子棋 - 双人对战版")

# 实例化棋盘界面（此时棋盘内部已经包含了轮流落子的逻辑）
board_ui = BoardUI(root, board_size=8, cell_size=60, margin=30)

# 启动 Tkinter 主循环，等待玩家点击
root.mainloop()