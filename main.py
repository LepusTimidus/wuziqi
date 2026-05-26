import tkinter as tk
from chessboard import BoardUI
from ai_chessboard import AIGameBoard  # 导入人机对战棋盘
from tkinter import messagebox


class GameModeSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("五子棋 - 模式选择")

        # 设置窗口大小
        window_width = 400
        window_height = 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # 创建标题标签
        title_label = tk.Label(root, text="五子棋游戏", font=("Arial", 20, "bold"))
        title_label.pack(pady=30)

        # 创建模式选择按钮
        self.pvp_button = tk.Button(root, text="人人对战", font=("Arial", 16),
                                    width=15, height=2, command=self.start_pvp_game)
        self.pvp_button.pack(pady=10)

        self.ai_button = tk.Button(root, text="人机对战", font=("Arial", 16),
                                   width=15, height=2, command=self.start_ai_game)
        self.ai_button.pack(pady=10)

    def start_pvp_game(self):
        # 销毁当前的选择界面
        self.root.destroy()
        # 创建新的窗口用于游戏
        game_window = tk.Tk()
        game_window.title("五子棋 - 双人对战版")
        board_ui = BoardUI(game_window, board_size=15, cell_size=40, margin=30)
        game_window.mainloop()

    def start_ai_game(self):
        # 销毁当前的选择界面
        self.root.destroy()
        # 创建新的窗口用于人机对战游戏
        game_window = tk.Tk()
        game_window.title("五子棋 - 人机对战版")
        ai_board_ui = AIGameBoard(game_window, board_size=15, cell_size=40, margin=30)
        game_window.mainloop()


# 创建主窗口并启动模式选择界面
if __name__ == "__main__":
    root = tk.Tk()
    app = GameModeSelector(root)
    root.mainloop()