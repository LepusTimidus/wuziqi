import tkinter as tk
from game_logic import GameLogic
from tkinter import messagebox
import random


class AIPlayer:
    def __init__(self, color="white"):
        self.color = color
        self.opponent_color = "black" if color == "white" else "white"
        # 定义不同棋型的权重分数
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
        """
        评估在 (row, col) 落子对 player_color 的价值
        结合了进攻得分和防守得分
        """
        score = 0
        stone_value = 1 if player_color == "black" else 2
        opponent_value = 2 if player_color == "black" else 1

        # 检查四个方向：水平、垂直、主对角线、副对角线
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            # 分析该方向上的连子情况
            my_count, my_empty_ends = self.analyze_line(game_logic, row, col, dr, dc, stone_value)
            opp_count, opp_empty_ends = self.analyze_line(game_logic, row, col, dr, dc, opponent_value)

            # --- 进攻评分 (自己下这步棋能形成什么棋型) ---
            score += self.get_shape_score(my_count, my_empty_ends) * 1.0

            # --- 防守评分 (如果不挡，对手下一步能形成什么棋型) ---
            # 如果对手在这个方向有巨大威胁，必须优先阻挡
            if opp_count >= 3:
                score += self.get_shape_score(opp_count, opp_empty_ends) * 1.2  # 防守权重略高

        return score

    def analyze_line(self, game_logic, row, col, dr, dc, value):
        """
        分析单个方向上的棋型
        返回 (连续棋子数, 空位端点数)
        """
        count = 0  # 连续同色棋子数量
        empty_ends = 0  # 两端的空位数量 (用于判断是"活"还是"眠")

        # 正方向查找
        r, c = row + dr, col + dc
        while 0 <= r <= game_logic.board_size and 0 <= c <= game_logic.board_size:
            if game_logic.board[r][c] == value:
                count += 1
            elif game_logic.board[r][c] == 0:  # 空位
                empty_ends += 1
                break
            else:
                break  # 遇到敌方棋子
            r += dr
            c += dc

        # 反方向查找
        r, c = row - dr, col - dc
        while 0 <= r <= game_logic.board_size and 0 <= c <= game_logic.board_size:
            if game_logic.board[r][c] == value:
                count += 1
            elif game_logic.board[r][c] == 0:  # 空位
                empty_ends += 1
                break
            else:
                break
            r -= dr
            c -= dc

        return count, empty_ends

    def get_shape_score(self, count, empty_ends):
        """
        根据连子数和空位端点数返回分数
        """
        if count >= 5:
            return self.shape_scores["FIVE"]
        elif count == 4:
            if empty_ends >= 1:  # 至少一端有空（实际是活四，因为另一端可能没路了，但在AI眼里是机会）
                return self.shape_scores["FOUR"]
            else:  # 两端都被堵死，虽然概率极低，但算作冲四
                return self.shape_scores["SLEEP_FOUR"]
        elif count == 3:
            if empty_ends >= 2:  # 两端都活 (活三)
                return self.shape_scores["THREE"]
            else:  # 一端被堵 (眠三)
                return self.shape_scores["SLEEP_THREE"]
        elif count == 2:
            if empty_ends >= 2:
                return self.shape_scores["TWO"]
            else:
                return self.shape_scores["SLEEP_TWO"]
        elif count == 1:
            return 10
        else:
            return 0

    def get_best_move(self, game_logic):
        """
        获取最佳移动位置 (困难模式)
        """
        best_score = -1
        best_move = None

        # 寻找所有空位，但优先考虑已有棋子附近
        empty_positions = []
        has_stones = False
        for row in range(game_logic.board_size + 1):
            for col in range(game_logic.board_size + 1):
                if game_logic.board[row][col] != 0:  # 找到已有棋子
                    has_stones = True
                    # 将周围2格范围内的空位加入候选
                    for r in range(row - 2, row + 3):
                        for c in range(col - 2, col + 3):
                            if (0 <= r <= game_logic.board_size and
                                    0 <= c <= game_logic.board_size and
                                    game_logic.is_empty(r, c)):
                                if (r, c) not in empty_positions:
                                    empty_positions.append((r, c))

        # 如果是开局（棋盘无子）或未找到附近空位，使用全盘扫描或中心开局
        if not empty_positions or not has_stones:
            center = game_logic.board_size // 2
            # 先尝试中心点
            if game_logic.is_empty(center, center):
                return center, center
            # 再尝试中心周围
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    r, c = center + dr, center + dc
                    if 0 <= r <= game_logic.board_size and 0 <= c <= game_logic.board_size and game_logic.is_empty(r,
                                                                                                                   c):
                        empty_positions.append((r, c))

        # 评估候选位置得分
        for row, col in empty_positions:
            # 进攻得分：AI自己下这里
            attack_score = self.evaluate_position(game_logic, row, col, self.color)

            # 防守得分：假设对手下这里
            defend_score = self.evaluate_position(game_logic, row, col, self.opponent_color)

            # 综合得分：防守权重略高，因为五子棋输赢就在一瞬间
            total_score = attack_score * 0.9 + defend_score * 1.1

            if total_score > best_score:
                best_score = total_score
                best_move = (row, col)

        # 如果实在没找到（极小概率），返回中心
        if best_move is None:
            center = game_logic.board_size // 2
            return center, center

        return best_move


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
        self.score_label = tk.Label(master, text="黑棋得分: 0 | 白棋得分: 0", font=("Arial", 14), fg="blue")
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

                # 检查人类玩家是否获胜
                winner = self.game_logic.check_win(row, col)
                if winner:
                    self.game_logic.game_over = True
                    self.canvas.unbind("<Button-1>")

                    # 更新得分
                    if winner == "black":
                        self.black_score += 1
                    else:
                        self.white_score += 1
                    self.score_label.config(text=f"黑棋得分: {self.black_score} | 白棋得分: {self.white_score}")

                    messagebox.showinfo("游戏结束", f"恭喜 {winner} 获胜！")
                    return

                # 切换到AI回合
                self.is_ai_turn = True
                self.status_label.config(text="AI正在思考...")
                self.master.after(500, self.ai_move)  # 延迟执行，模拟思考

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

                    # 更新得分
                    if winner == "black":
                        self.black_score += 1
                    else:
                        self.white_score += 1
                    self.score_label.config(text=f"黑棋得分: {self.black_score} | 白棋得分: {self.white_score}")

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
        # 1. 清空画布
        self.canvas.delete("all")
        # 2. 重绘棋盘
        self.draw_board()
        # 3. 重置逻辑
        self.game_logic.reset()
        # 4. 恢复初始状态
        self.current_player = "black"
        self.is_ai_turn = False
        self.status_label.config(text="轮到黑棋落子")
        # 5. 重新绑定事件
        self.canvas.bind("<Button-1>", self.on_click)

    def reset_score(self):
        self.black_score = 0
        self.white_score = 0
        self.score_label.config(text="黑棋得分: 0 | 白棋得分: 0")