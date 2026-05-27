import tkinter as tk
from chessboard import BoardUI
from ai_chessboard import AIGameBoard


class GameModeSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("五子棋 - 模式选择")
        window_width = 400
        window_height = 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        title_label = tk.Label(root, text="五子棋游戏", font=("Arial", 20, "bold"))
        title_label.pack(pady=30)

        # 双人对战按钮
        self.pvp_button = tk.Button(root, text="人人对战", font=("Arial", 16), width=15, height=2,
                                    command=self.start_pvp_game)
        self.pvp_button.pack(pady=10)

        # 人机对战按钮（点击后进入难度选择）
        self.ai_button = tk.Button(root, text="人机对战", font=("Arial", 16), width=15, height=2,
                                   command=self.open_ai_difficulty)
        self.ai_button.pack(pady=10)

    def start_pvp_game(self):
        self.root.destroy()
        game_window = tk.Tk()
        game_window.title("五子棋 - 双人对战版")
        board_ui = BoardUI(game_window, board_size=15, cell_size=40, margin=30)
        game_window.mainloop()

    def open_ai_difficulty(self):
        # 打开难度选择窗口
        self.root.withdraw()  # 隐藏主窗口，而不是销毁
        difficulty_window = tk.Toplevel(self.root)
        DifficultySelector(difficulty_window, self)


class DifficultySelector:
    def __init__(self, window, main_app):
        self.window = window
        self.main_app = main_app
        self.window.title("选择难度")
        self.window.geometry("300x250")

        # 居中显示
        self.window.geometry(f"+{int(self.main_app.root.winfo_x() + 50)}+{int(self.main_app.root.winfo_y() + 100)}")

        tk.Label(self.window, text="请选择 AI 难度", font=("Arial", 16, "bold"), pady=20).pack()

        # 难度按钮
        tk.Button(self.window, text="简单", font=("Arial", 14), width=10,
                  command=lambda: self.start_ai_game("easy")).pack(pady=5)
        tk.Button(self.window, text="中等", font=("Arial", 14), width=10,
                  command=lambda: self.start_ai_game("medium")).pack(pady=5)
        tk.Button(self.window, text="困难", font=("Arial", 14), width=10,
                  command=lambda: self.start_ai_game("hard")).pack(pady=5)

        # 返回按钮
        tk.Button(self.window, text="返回", command=self.go_back).pack(pady=10)

    def start_ai_game(self, difficulty):
        self.window.destroy()
        self.main_app.root.destroy()  # 完全关闭初始窗口
        game_window = tk.Tk()
        game_window.title(f"五子棋 - 人机对战 [{difficulty}]")
        # 将难度传给 AIGameBoard
        ai_board_ui = AIGameBoard(game_window, board_size=15, cell_size=40, margin=30, difficulty=difficulty)
        game_window.mainloop()

    def go_back(self):
        self.window.destroy()
        self.main_app.root.deiconify()  # 显示主窗口


if __name__ == "__main__":
    root = tk.Tk()
    app = GameModeSelector(root)
    root.mainloop()