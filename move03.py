import os
import tkinter as tk
from PIL import Image,ImageTk

#>>ディレクトリ>>
cwd = os.getcwd()


#>>ウィンドウ、キャンバス>>
CANVAS_WIDTH = 160 #キャンバス幅
CANVAS_HEIGHT = 200 #キャンバス高さ
MARGINE_X = 2 #マージン
MARGINE_Y = 2 #マージン
CANVAS_SIZE = f"{CANVAS_WIDTH+MARGINE_X}x{CANVAS_HEIGHT+MARGINE_Y}"#キャンバスサイズ

#ウィンドウ設置
root = tk.Tk()
root.title("アニメーション")
root.geometry(CANVAS_SIZE)

#キャンバス設置
canvas = tk.Canvas(root,width = CANVAS_WIDTH,height = CANVAS_HEIGHT,bg = "skyblue")
canvas.pack()


#>>キャラクター>>
CHARA_WIDTH = 64  #キャラの幅
CHARA_HEIGHT = 96 #キャラの高さ

#キャラクターの座標
charaX = 60 
charaY = 60 
charaD = 1  #キャラの向き
FRAME_LIST = [0,1,2,1]

moveCount = 0    #移動カウンタ 0から3の4段階

#ゲームの基本となる1ティック時間(ms)
TICK_TIME = 100

#キャラチップを1毎の画像に並べたキャラシートを読み込む
CHARA_SHEET = Image.open(cwd+"/img/character.png")

#読み込んだ画像から縦横何枚ずつチップがあるか求める
CHARA_X = CHARA_SHEET.width // CHARA_WIDTH
CHARA_Y = CHARA_SHEET.height // CHARA_HEIGHT


#キャラチップに分割し2次元配列に格納する
CHARA_CHIP = []
#キャラシートの列数だけ繰り返す
for j in range(CHARA_Y): 
    #新しい行を作成
    row = []
    
    #キャラシートの行数だけ繰り返す
    for i in range(CHARA_X): 
        # キャラクターのチップを切り出して画像を作成
        image = ImageTk.PhotoImage(CHARA_SHEET.crop((
            CHARA_WIDTH * i,               # 左上のX座標
            CHARA_HEIGHT * j,              # 左上のY座標
            CHARA_WIDTH * (i + 1),         # 右下のX座標
            CHARA_HEIGHT * (j + 1)         # 右下のY座標
        )))
        
        # 作成した画像を行に追加
        row.append(image)
    
    # 行をCHARA_CHIPに追加
    CHARA_CHIP.append(row)


#キャラクターを再描写する関数
def setChara(x,y,d,frame):
    """
    x:キャラのX座標
    y:キャラのY座標
    d:キャラの向き
    frame:コマ数
    """
    #キャラの画像を選択
    img = CHARA_CHIP[d][FRAME_LIST[frame]]
    
    #今の画像を消して再描写
    canvas.delete("chara")
    canvas.create_image(x,y,image =img ,tag="chara",anchor=tk.NW)


#>>ゲームのメインループ関数>>
def gameLoop():
    global charaX,charaY,charaD,moveCount
    
    setChara(charaX,charaY,charaD,moveCount)
    
    if moveCount==3:#アニメーションが最終コマならば
        moveCount = 0
    else:
        moveCount += 1
    
    root.after(TICK_TIME,gameLoop)

setChara(charaX,charaY,charaD,1)

gameLoop()
print("start!")
root.mainloop()