import tkinter as tk
from game_logic import GameLogic

class BoardUI:
    def __init__(self, master, board_size=8, cell_size=60, margin=30):
        self.master = master
        self.BOARD_SIZE = board_size
        self.CELL_SIZE = cell_size
        self.MARGIN = margin
        
        self.game_logic = GameLogic(board_size)
        
        # 初始化当前玩家为黑棋
        self.current_player = "black" 

        canvas_size = (board_size * cell_size) + (margin * 2)
        self.canvas = tk.Canvas(master, width=canvas_size, height=canvas_size, bg="#DEB887")
        self.canvas.pack()
        
        # 状态栏，显示当前轮到谁
        self.status_label = tk.Label(master, text="轮到黑棋落子", font=("Arial", 14))
        self.status_label.pack()
        
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

        # 计算点击的棋盘坐标
        col = (event.x - self.MARGIN + self.CELL_SIZE // 2) // self.CELL_SIZE
        row = (event.y - self.MARGIN + self.CELL_SIZE // 2) // self.CELL_SIZE
        
        if 0 <= row <= self.BOARD_SIZE and 0 <= col <= self.BOARD_SIZE:
            # 使用当前玩家的颜色落子
            if self.game_logic.place_stone(row, col, self.current_player):
                self.draw_stone(row, col, self.current_player)
                
                # 检查是否获胜
                winner = self.game_logic.check_win(row, col)
                if winner:
                    self.game_logic.game_over = True
                    self.canvas.unbind("<Button-1>")
                    from tkinter import messagebox
                    messagebox.showinfo("游戏结束", f"恭喜 {winner} 获胜！")
                    return 
                
                # 落子成功且未分胜负，切换玩家
                self.switch_player()

    def draw_stone(self, row, col, color):
        center_x = self.MARGIN + col * self.CELL_SIZE
        center_y = self.MARGIN + row * self.CELL_SIZE
        radius = self.CELL_SIZE * 0.4
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