import tkinter as tk
from game_logic import GameLogic
from tkinter import messagebox
import random


class AIPlayer:
    def __init__(self, color="white"):
        self.color = color
        self.opponent_color = "black" if color == "white" else "white"

    def evaluate_position(self, game_logic, row, col, player_color):
        """评估某个位置的得分"""
        score = 0
        stone_value = 1 if player_color == "black" else 2
        opponent_value = 2 if player_color == "black" else 1

        # 检查四个方向：水平、垂直、对角线
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            # 统计连续同色棋子数量
            count = 1
            # 向正方向查找
            r, c = row + dr, col + dc
            while (0 <= r <= game_logic.board_size and
                   0 <= c <= game_logic.board_size and
                   game_logic.board[r][c] == stone_value):
                count += 1
                r += dr
                c += dc

            # 向反方向查找
            r, c = row - dr, col - dc
            while (0 <= r <= game_logic.board_size and
                   0 <= c <= game_logic.board_size and
                   game_logic.board[r][c] == stone_value):
                count += 1
                r -= dr
                c -= dc

            # 根据连成的数量评分
            if count >= 5:
                score += 100000  # 成五
            elif count == 4:
                score += 10000  # 活四
            elif count == 3:
                score += 1000  # 活三
            elif count == 2:
                score += 100  # 活二

        # 检查防守分数（阻止对手获胜）
        for dr, dc in directions:
            count = 1
            # 向正方向查找对手棋子
            r, c = row + dr, col + dc
            while (0 <= r <= game_logic.board_size and
                   0 <= c <= game_logic.board_size and
                   game_logic.board[r][c] == opponent_value):
                count += 1
                r += dr
                c += dc

            # 向反方向查找对手棋子
            r, c = row - dr, col - dc
            while (0 <= r <= game_logic.board_size and
                   0 <= c <= game_logic.board_size and
                   game_logic.board[r][c] == opponent_value):
                count += 1
                r -= dr
                c -= dc

            # 根据对手连成的数量评分
            if count >= 4:
                score += 50000  # 阻止对手成五
            elif count == 3:
                score += 5000  # 阻止对手活三
            elif count == 2:
                score += 500  # 阻止对手活二

        return score

    def get_best_move(self, game_logic):
        """获取最佳移动位置"""
        best_score = -1
        best_move = None

        # 寻找所有空位
        empty_positions = []
        for row in range(game_logic.board_size + 1):
            for col in range(game_logic.board_size + 1):
                if game_logic.is_empty(row, col):
                    empty_positions.append((row, col))

        # 如果棋盘为空，放在中心位置
        if not empty_positions:
            center = game_logic.board_size // 2
            return center, center

        # 随机选择几个位置进行评估（优化性能）
        if len(empty_positions) > 50:
            empty_positions = random.sample(empty_positions, 50)

        # 评估每个空位的得分
        for row, col in empty_positions:
            # 临时放置棋子评估得分
            score = self.evaluate_position(game_logic, row, col, self.color)

            # 也考虑放置对手棋子的影响
            temp_score = self.evaluate_position(game_logic, row, col, self.opponent_color)
            score += temp_score * 0.8  # 给防守加权

            if score > best_score:
                best_score = score
                best_move = (row, col)

        return best_move if best_move else (game_logic.board_size // 2, game_logic.board_size // 2)


class AIGameBoard:
    def __init__(self, master, board_size=15, cell_size=40, margin=30):
        self.master = master
        self.BOARD_SIZE = board_size
        self.CELL_SIZE = cell_size
        self.MARGIN = margin

        self.game_logic = GameLogic(board_size)
        self.ai_player = AIPlayer("white")  # AI执白棋

        # 初始化当前玩家为黑棋（人类玩家）
        self.current_player = "black"
        self.is_ai_turn = False

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
        if self.game_logic.game_over or self.is_ai_turn:
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

                    # 切换到AI回合
                self.is_ai_turn = True
                self.status_label.config(text="AI正在思考...")
                self.master.after(500, self.ai_move)  # 延迟一下，让AI看起来像在思考

    def ai_move(self):
        if not self.game_logic.game_over:
            # 获取AI的最佳移动
            ai_row, ai_col = self.ai_player.get_best_move(self.game_logic)

            if ai_row is not None and ai_col is not None:
                # AI落子
                self.game_logic.place_stone(ai_row, ai_col, "white")
                self.draw_stone(ai_row, ai_col, "white")

                # 检查AI是否获胜
                winner = self.game_logic.check_win(ai_row, ai_col)
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

                # 切换回人类玩家回合
                self.is_ai_turn = False
                self.current_player = "black"
                self.status_label.config(text="轮到黑棋落子")
            else:
                # 如果AI无法找到合适的位置，则结束游戏
                self.game_logic.game_over = True
                messagebox.showinfo("游戏结束", "棋盘已满，平局！")

    def draw_stone(self, row, col, color):
        center_x = self.MARGIN + col * self.CELL_SIZE
        center_y = self.MARGIN + row * self.CELL_SIZE
        radius = self.CELL_SIZE * 0.3  # 缩小棋子半径，使其看起来更美观
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill=color, outline="black"
        )

    def reset_board(self):
        # 1. 清空画布上的所有元素
        self.canvas.delete("all")
        # 2. 重新绘制棋盘线（因为 delete("all") 会把线也删掉）
        self.draw_board()

        # 3. 重置游戏逻辑状态
        self.game_logic.reset()

        # 4. 恢复初始状态
        self.current_player = "black"
        self.is_ai_turn = False
        self.status_label.config(text="轮到黑棋落子")

        # 5. 重新绑定鼠标点击事件，让棋盘恢复可点击
        self.canvas.bind("<Button-1>", self.on_click)

    def reset_score(self):
        self.black_score = 0
        self.white_score = 0
        self.score_label.config(text="黑棋得分: 0  |  白棋得分: 0")