import tkinter as tk
from game_logic import GameLogic  # 导入刚刚写的逻辑类

class BoardUI:
    def __init__(self, master, board_size=8, cell_size=60, margin=30):
        self.master = master
        self.BOARD_SIZE = board_size
        self.CELL_SIZE = cell_size
        self.MARGIN = margin
        
        # 实例化游戏逻辑对象
        self.game_logic = GameLogic(board_size)

        canvas_size = (board_size * cell_size) + (margin * 2)
        self.canvas = tk.Canvas(master, width=canvas_size, height=canvas_size, bg="#DEB887")
        self.canvas.pack()
        
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        for i in range(self.BOARD_SIZE + 1):
            # 横线
            start_x = self.MARGIN
            end_x = self.MARGIN + self.BOARD_SIZE * self.CELL_SIZE
            y = self.MARGIN + i * self.CELL_SIZE
            self.canvas.create_line(start_x, y, end_x, y, fill="black")
            # 竖线
            start_y = self.MARGIN
            end_y = self.MARGIN + self.BOARD_SIZE * self.CELL_SIZE
            x = self.MARGIN + i * self.CELL_SIZE
            self.canvas.create_line(x, start_y, x, end_y, fill="black")

    def on_click(self, event):
        # 如果游戏已经结束，直接返回，不处理点击
        if self.game_logic.game_over:
            return

        col = (event.x - self.MARGIN + self.CELL_SIZE // 2) // self.CELL_SIZE
        row = (event.y - self.MARGIN + self.CELL_SIZE // 2) // self.CELL_SIZE
        
        if 0 <= row <= self.BOARD_SIZE and 0 <= col <= self.BOARD_SIZE:
            if self.game_logic.place_stone(row, col, "black"):
                self.draw_stone(row, col, "black")
                
                winner = self.game_logic.check_win(row, col)
                if winner:
                    self.game_logic.game_over = True  # 标记游戏结束
                    print(f"🎉 恭喜！{winner} 获胜！游戏结束！")
                    self.canvas.unbind("<Button-1>") # 禁止玩家继续点击
                    from tkinter import messagebox
                    messagebox.showinfo("游戏结束", f"恭喜 {winner} 获胜！")

    def draw_stone(self, row, col, color):
        center_x = self.MARGIN + col * self.CELL_SIZE
        center_y = self.MARGIN + row * self.CELL_SIZE
        radius = self.CELL_SIZE * 0.4
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill=color, outline="black"
        )

    #虽然叫ai但是其实是一个外部的通用接口
    def ai_place_stone(self, row, col):
        # AI落子前也检查一下，如果游戏结束了就直接返回
        if self.game_logic.game_over:
            return False

        if self.game_logic.place_stone(row, col, "white"):
            self.draw_stone(row, col, "white")
            
            winner = self.game_logic.check_win(row, col)
            if winner:
                self.game_logic.game_over = True  # 标记游戏结束
                print(f"🤖 AI 获胜！游戏结束！")
                from tkinter import messagebox
                messagebox.showinfo("游戏结束", f"AI 获胜！")
                self.canvas.unbind("<Button-1>")
            return True
        else:
            return False