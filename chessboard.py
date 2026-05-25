import tkinter as tk

root = tk.Tk()
root.title("棋盘界面")

BOARD_SIZE = 8  # 8x8棋盘
CELL_SIZE = 60  # 每个格子大小
canvas = tk.Canvas(root, width=BOARD_SIZE * CELL_SIZE, height=BOARD_SIZE * CELL_SIZE)
canvas.pack()

# 画棋盘
for row in range(BOARD_SIZE):
    for col in range(BOARD_SIZE):
        x1 = col * CELL_SIZE
        y1 = row * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        color = "white"

        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

root.mainloop()