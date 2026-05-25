class GameLogic:
    def __init__(self, board_size=8):
        self.board_size = board_size
        self.game_over = False  # 新增：游戏是否结束的标志
        # 初始化棋盘数据，0代表空，1代表黑棋，2代表白棋
        self.board = [[0] * (board_size + 1) for _ in range(board_size + 1)]

    def is_empty(self, row, col):
        # 如果游戏已经结束，或者坐标不合法，或者该位置不为0，都返回False
        if self.game_over or not (0 <= row <= self.board_size and 0 <= col <= self.board_size):
            return False
        return self.board[row][col] == 0

    def place_stone(self, row, col, color):
        if self.is_empty(row, col):
            stone_value = 1 if color == "black" else 2
            self.board[row][col] = stone_value
            return True
        return False

    # check_win 方法保持不变，但在返回胜利者后，我们需要在主程序里把 game_over 设为 True
    def check_win(self, row, col):
        current_color = self.board[row][col]
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            # 向正方向查找
            r, c = row + dr, col + dc
            while (0 <= r <= self.board_size and 
                   0 <= c <= self.board_size and 
                   self.board[r][c] == current_color):
                count += 1
                r += dr
                c += dc
            # 向反方向查找
            r, c = row - dr, col - dc
            while (0 <= r <= self.board_size and 
                   0 <= c <= self.board_size and 
                   self.board[r][c] == current_color):
                count += 1
                r -= dr
                c -= dc
            
            if count >= 5:
                return "black" if current_color == 1 else "white"
        return None
    
    # 在 game_logic.py 的 GameLogic 类中
    def reset(self):
        self.board = [[0 for _ in range(self.board_size + 1)] for _ in range(self.board_size + 1)] # 清空棋盘数组
        self.game_over = False  # 将游戏结束标志设为 False