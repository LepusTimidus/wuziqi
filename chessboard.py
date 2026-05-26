import tkinter as tk
from game_logic import GameLogic
from tkinter import messagebox


class BoardUI:
    def __init__(self, master, board_size=15, cell_size=40, margin=30):  # 修改为15x15棋盘，缩小cell_size
        self.master = master
        self.BOARD_SIZE = board_size
        self.CELL_SIZE = cell_size
        self.MARGIN = margin

        self.game_logic = GameLogic(board_size)

        # 初始化当前玩家为黑棋
        self.current_player = "black"

        # 初始化双方得分
        self.black_score = 0
        self.white_score = 0

        canvas_size = (board_size * cell_size) + (margin * 2)
        self.canvas = tk.Canvas(master, width=canvas_size, height=canvas_size, bg="#DEB887")
        self.canvas.pack()

        # 计分显示标签
        self.score_label = tk.Label(master, text="黑棋得分: 0  |  白棋得分: 0", font=("Arial", 14), fg="blue")
        self.score_label.pack()

        # 状态栏
        self.status_label = tk.Label(master, text="轮到黑棋落子", font=("Arial", 14))
        self.status_label.pack()

        # --- 新增：重置棋盘按钮 ---
        self.reset_board_btn = tk.Button(master, text="重置棋盘", font=("Arial", 12), command=self.reset_board)
        self.reset_board_btn.pack(pady=5)

        # 重置得分按钮
        self.reset_score_btn = tk.Button(master, text="重置得分", font=("Arial", 12), command=self.reset_score)
        self.reset_score_btn.pack(pady=5)

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        for i in range(self.BOARD_SIZE + 1):
            # 画横线
            start_x = self.MARGIN
            end_x = self.MARGIN + self.BOARD_SIZE * self.CELL_SIZE
            y = self.MARGIN + i * self.CELL_SIZE
            self.canvas.create_line(start_x, y, end_x, y, fill="black")
            # 画竖线
            start_y = self.MARGIN
            end_y = self.MARGIN + self.BOARD_SIZE * self.CELL_SIZE
            x = self.MARGIN + i * self.CELL_SIZE
            self.canvas.create_line(x, start_y, x, end_y, fill="black")

    def on_click(self, event):
        if self.game_logic.game_over:
            return

        col = (event.x - self.MARGIN + self.CELL_SIZE // 2) // self.CELL_SIZE
        row = (event.y - self.MARGIN + self.CELL_SIZE // 2) // self.CELL_SIZE

        if 0 <= row <= self.BOARD_SIZE and 0 <= col <= self.BOARD_SIZE:
            if self.game_logic.place_stone(row, col, self.current_player):
                self.draw_stone(row, col, self.current_player)

                winner = self.game_logic.check_win(row, col)
                if winner:
                    self.game_logic.game_over = True
                    self.canvas.unbind("<Button-1>")

                    # --- 新增：给获胜方加分并更新界面 ---
                    if winner == "black":
                        self.black_score += 1
                    else:
                        self.white_score += 1
                    self.score_label.config(text=f"黑棋得分: {self.black_score}  |  白棋得分: {self.white_score}")

                    messagebox.showinfo("游戏结束", f"恭喜 {winner} 获胜！")
                    return

                self.switch_player()

    def draw_stone(self, row, col, color):
        center_x = self.MARGIN + col * self.CELL_SIZE
        center_y = self.MARGIN + row * self.CELL_SIZE
        radius = self.CELL_SIZE * 0.3  # 缩小棋子半径，使其看起来更美观
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill=color, outline="black"
        )

    def switch_player(self):
        if self.current_player == "black":
            self.current_player = "white"
            self.status_label.config(text="轮到白棋落子")
        else:
            self.current_player = "black"
            self.status_label.config(text="轮到黑棋落子")

    def reset_board(self):
        # 1. 清空画布上的所有元素
        self.canvas.delete("all")
        # 2. 重新绘制棋盘线（因为 delete("all") 会把线也删掉）
        self.draw_board()

        # 3. 重置游戏逻辑状态（假设你的 GameLogic 类里有一个 reset 方法）
        self.game_logic.reset()

        # 4. 恢复初始状态
        self.current_player = "black"
        self.status_label.config(text="轮到黑棋落子")

        # 5. 重新绑定鼠标点击事件，让棋盘恢复可点击
        self.canvas.bind("<Button-1>", self.on_click)

    def reset_score(self):
        self.black_score = 0
        self.white_score = 0
        self.score_label.config(text="黑棋得分: 0  |  白棋得分: 0")