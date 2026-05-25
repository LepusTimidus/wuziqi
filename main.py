import tkinter as tk
import random
from chessboard import BoardUI

root = tk.Tk()
root.title("五子棋 - 防重复落子版")

board_ui = BoardUI(root, board_size=8, cell_size=60, margin=30)

def ai_move():
    # 如果游戏已经结束，AI 直接停止运行
    if board_ui.game_logic.game_over:
        return

    while True:
        random_row = random.randint(0, board_ui.BOARD_SIZE)
        random_col = random.randint(0, board_ui.BOARD_SIZE)
        if board_ui.ai_place_stone(random_row, random_col):
            break
    
    # 只有游戏没结束时，才继续安排下一次AI落子
    if not board_ui.game_logic.game_over:
        root.after(1000, ai_move)

# 启动 AI 模拟落子
root.after(1000, ai_move)

# 启动 Tkinter 主循环（必须有这句，窗口才会弹出来！）
root.mainloop()