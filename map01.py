import os
import tkinter as tk

#>>ディレクトリ>>
cwd = os.getcwd()

#>>マップ設定>>
CHIP_SIZE = 64 #マップチップの大きさ
X_MAPSIZE = 20 #マップのx方向タイル数
Y_MAPSIZE = 10 #マップのy方向タイル数

#>>ウィンドウ、キャンバス>>
CANVAS_WIDTH = CHIP_SIZE * X_MAPSIZE #キャンバス幅
CANVAS_HEIGHT = CHIP_SIZE * Y_MAPSIZE #キャンバス高さ
MARGINE_X = 2 #マージン
MARGINE_Y = 2 #マージン
CANVAS_SIZE = f"{CANVAS_WIDTH+MARGINE_X}x{CANVAS_HEIGHT+MARGINE_Y}"#キャンバスサイズ

#ウィンドウ設置
root = tk.Tk()
root.title("マップ表示")
root.geometry(CANVAS_SIZE)

#キャンバス設置
canvas = tk.Canvas(root,width = CANVAS_WIDTH,height = CANVAS_HEIGHT,bg = "skyblue")
canvas.pack()


#>>マップチップ>>
MAP_CHIP = [
    tk.PhotoImage(file = cwd+"/img/grass.png"),
    tk.PhotoImage(file = cwd+"/img/sand.png"),
    tk.PhotoImage(file = cwd+"/img/water.png")
    ]

canvas.create_image(0,0,image =MAP_CHIP[0] ,tag="chip1",anchor=tk.NW)

root.mainloop()