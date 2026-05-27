import tkinter as tk
from game_logic import GameLogic
from tkinter import messagebox
import random


class AIPlayer:
    def __init__(self, color="white", difficulty="hard"):
        self.color = color
        self.opponent_color = "black" if color == "white" else "white"
        self.difficulty = difficulty  # 记录难度: "easy", "medium", "hard"

        # 定义不同棋型的权重分数 (困难模式专用)
        self.shape_scores = {
            "FIVE": 1000000000,  # 连五 (胜利)
            "FOUR": 100000000,  # 活四 (必胜)
            "SLEEP_FOUR": 10000000,  # 冲四 (一端被堵)
            "THREE": 1000000,  # 活三
            "SLEEP_THREE": 10000,  # 眠三
            "TWO": 1000,  # 活二
            "SLEEP_TWO": 100  # 眠二
        }

    def evaluate_position(self, game_logic, row, col, player_color):
        score = 0
        stone_value = 1 if player_color == "black" else 2
        opponent_value = 2 if player_color == "black" else 1
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            my_count, my_empty_ends = self.analyze_line(game_logic, row, col, dr, dc, stone_value)
            opp_count, opp_empty_ends = self.analyze_line(game_logic, row, col, dr, dc, opponent_value)

            # 进攻评分
            score += self.get_shape_score(my_count, my_empty_ends) * 1.0
            # 防守评分
            if opp_count >= 3:
                score += self.get_shape_score(opp_count, opp_empty_ends) * 1.2
        return score

    def analyze_line(self, game_logic, row, col, dr, dc, value):
        count = 0
        empty_ends = 0
        # 正方向
        r, c = row + dr, col + dc
        while 0 <= r <= game_logic.board_size and 0 <= c <= game_logic.board_size:
            if game_logic.board[r][c] == value:
                count += 1
            elif game_logic.board[r][c] == 0:
                empty_ends += 1
                break
            else:
                break
            r += dr
            c += dc
        # 反方向
        r, c = row - dr, col - dc
        while 0 <= r <= game_logic.board_size and 0 <= c <= game_logic.board_size:
            if game_logic.board[r][c] == value:
                count += 1
            elif game_logic.board[r][c] == 0:
                empty_ends += 1
                break
            else:
                break
            r -= dr
            c -= dc
        return count, empty_ends

    def get_shape_score(self, count, empty_ends):
        if count >= 5:
            return self.shape_scores["FIVE"]
        elif count == 4:
            return self.shape_scores["FOUR"] if empty_ends >= 1 else self.shape_scores["SLEEP_FOUR"]
        elif count == 3:
            return self.shape_scores["THREE"] if empty_ends >= 2 else self.shape_scores["SLEEP_THREE"]
        elif count == 2:
            return self.shape_scores["TWO"] if empty_ends >= 2 else self.shape_scores["SLEEP_TWO"]
        elif count == 1:
            return 10
        else:
            return 0

    def get_best_move(self, game_logic):
        # --- 简单模式逻辑 ---
        if self.difficulty == "easy":
            # 50% 概率随机乱下，50% 概率正常思考
            if random.random() < 0.5:
                all_empty = [(r, c) for r in range(game_logic.board_size + 1)
                             for c in range(game_logic.board_size + 1) if game_logic.is_empty(r, c)]
                if all_empty:
                    return random.choice(all_empty)

        # --- 中等模式逻辑 ---
        search_radius = 2  # 困难和中等默认搜索半径
        if self.difficulty == "medium":
            search_radius = 1  # 中等难度只看周围1格，视野变窄

        best_score = -1
        best_move = None
        empty_positions = []
        has_stones = False

        for row in range(game_logic.board_size + 1):
            for col in range(game_logic.board_size + 1):
                if game_logic.board[row][col] != 0:
                    has_stones = True
                    for r in range(row - search_radius, row + search_radius + 1):
                        for c in range(col - search_radius, col + search_radius + 1):
                            if (0 <= r <= game_logic.board_size and
                                    0 <= c <= game_logic.board_size and
                                    game_logic.is_empty(r, c)):
                                if (r, c) not in empty_positions:
                                    empty_positions.append((r, c))

        if not empty_positions or not has_stones:
            center = game_logic.board_size // 2
            if game_logic.is_empty(center, center):
                return center, center
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    r, c = center + dr, center + dc
                    if 0 <= r <= game_logic.board_size and 0 <= c <= game_logic.board_size and game_logic.is_empty(r,
                                                                                                                   c):
                        empty_positions.append((r, c))

        for row, col in empty_positions:
            attack_score = self.evaluate_position(game_logic, row, col, self.color)
            defend_score = self.evaluate_position(game_logic, row, col, self.opponent_color)

            # 困难和简单模式保持原有攻防权重
            attack_weight, defend_weight = 0.9, 1.1

            # --- 中等模式削弱防守 ---
            if self.difficulty == "medium":
                defend_weight = 0.6  # 降低防守意识，更容易被玩家突破

            total_score = attack_score * attack_weight + defend_score * defend_weight

            if total_score > best_score:
                best_score = total_score
                best_move = (row, col)

        if best_move is None:
            center = game_logic.board_size // 2
            return center, center
        return best_move


class AIGameBoard:
    # 增加 difficulty 参数，默认为 hard
    def __init__(self, master, board_size=15, cell_size=40, margin=30, difficulty="hard"):
        self.master = master
        self.BOARD_SIZE = board_size
        self.CELL_SIZE = cell_size
        self.MARGIN = margin
        self.game_logic = GameLogic(board_size)
        # 将难度传给 AI
        self.ai_player = AIPlayer("white", difficulty)

        self.current_player = "black"
        self.is_ai_turn = False
        self.black_score = 0
        self.white_score = 0

        canvas_size = (board_size * cell_size) + (margin * 2)
        self.canvas = tk.Canvas(master, width=canvas_size, height=canvas_size, bg="#DEB887")
        self.canvas.pack()

        # 显示当前难度
        diff_text = {"easy": "简单", "medium": "中等", "hard": "困难"}
        self.diff_label = tk.Label(master, text=f"当前难度: {diff_text.get(difficulty, '困难')}",
                                   font=("Arial", 14, "bold"), fg="red")
        self.diff_label.pack()

        self.score_label = tk.Label(master, text="黑棋得分: 0 | 白棋得分: 0", font=("Arial", 14), fg="blue")
        self.score_label.pack()

        self.status_label = tk.Label(master, text="轮到黑棋落子", font=("Arial", 14))
        self.status_label.pack()

        self.reset_board_btn = tk.Button(master, text="重置棋盘", font=("Arial", 12), command=self.reset_board)
        self.reset_board_btn.pack(pady=5)

        self.reset_score_btn = tk.Button(master, text="重置得分", font=("Arial", 12), command=self.reset_score)
        self.reset_score_btn.pack(pady=5)

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        for i in range(self.BOARD_SIZE + 1):
            start_x = self.MARGIN
            end_x = self.MARGIN + self.BOARD_SIZE * self.CELL_SIZE
            y = self.MARGIN + i * self.CELL_SIZE
            self.canvas.create_line(start_x, y, end_x, y, fill="black")
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
                    if winner == "black":
                        self.black_score += 1
                    else:
                        self.white_score += 1
                    self.score_label.config(text=f"黑棋得分: {self.black_score} | 白棋得分: {self.white_score}")
                    messagebox.showinfo("游戏结束", f"恭喜 {winner} 获胜！")
                    return

                self.is_ai_turn = True
                self.status_label.config(text="AI正在思考...")
                self.master.after(500, self.ai_move)

    def ai_move(self):
        if not self.game_logic.game_over:
            ai_row, ai_col = self.ai_player.get_best_move(self.game_logic)
            if ai_row is not None and ai_col is not None:
                self.game_logic.place_stone(ai_row, ai_col, "white")
                self.draw_stone(ai_row, ai_col, "white")
                winner = self.game_logic.check_win(ai_row, ai_col)
                if winner:
                    self.game_logic.game_over = True
                    self.canvas.unbind("<Button-1>")
                    if winner == "black":
                        self.black_score += 1
                    else:
                        self.white_score += 1
                    self.score_label.config(text=f"黑棋得分: {self.black_score} | 白棋得分: {self.white_score}")
                    messagebox.showinfo("游戏结束", f"恭喜 {winner} 获胜！")
                    return

                self.is_ai_turn = False
                self.current_player = "black"
                self.status_label.config(text="轮到黑棋落子")
            else:
                self.game_logic.game_over = True
                messagebox.showinfo("游戏结束", "棋盘已满，平局！")

    def draw_stone(self, row, col, color):
        center_x = self.MARGIN + col * self.CELL_SIZE
        center_y = self.MARGIN + row * self.CELL_SIZE
        radius = self.CELL_SIZE * 0.3
        self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, fill=color,
                                outline="black")

    def reset_board(self):
        self.canvas.delete("all")
        self.draw_board()
        self.game_logic.reset()
        self.current_player = "black"
        self.is_ai_turn = False
        self.status_label.config(text="轮到黑棋落子")
        self.canvas.bind("<Button-1>", self.on_click)

    def reset_score(self):
        self.black_score = 0
        self.white_score = 0
        self.score_label.config(text="黑棋得分: 0 | 白棋得分: 0")