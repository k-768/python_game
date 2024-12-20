import copy
import os
import tkinter as tk
from PIL import Image,ImageTk

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
#マップチップを1枚の画像に並べたマップシートを読み込む
MAP_SHEET = Image.open(cwd+"/img/sheet1.png")

#読み込んだ画像から縦横何枚ずつチップがあるか求める
CHIP_X = MAP_SHEET.width // CHIP_SIZE
CHIP_Y = MAP_SHEET.height // CHIP_SIZE

#マップシートをマップチップに分割し配列に格納する
MAP_CHIP = []

for y in range(CHIP_Y):
    for x in range(CHIP_X):
        image = ImageTk.PhotoImage(MAP_SHEET.crop((
            CHIP_SIZE*x , 
            CHIP_SIZE*y , 
            CHIP_SIZE*(x+1) , 
            CHIP_SIZE*(y+1)
            )))
        MAP_CHIP.append(image)


#>>マップデータ>>
MAP_DATA = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3],
    [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [2, 2, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]

#通行許可設定
#0:不可
#1:可能
PASSAGE_PERMIT = [0,1,1,0]

#釣り可能設定
#0:不可
#1:可能
FISHING_PERMIT = [0,0,0,1]

#>>マップ描画>>>
#マップチップを並べてマップを作成する関数
def mapping():
    for y in range(Y_MAPSIZE):
        for x in range(X_MAPSIZE):
            canvas.create_image(getRealCoord(x,y),image =MAP_CHIP[MAP_DATA[y][x]] ,tag=f"chip{x},{y}",anchor=tk.NW)

#マップ座標から画面座標に変換
def getRealCoord(mapx, mapy):
    return(mapx * CHIP_SIZE, mapy * CHIP_SIZE)


#>>アイコン>>
# 吹き出し
ICON = {
    "fishing" : ImageTk.PhotoImage(Image.open(cwd+"/img/fishing.png")),
    "hit" : ImageTk.PhotoImage(Image.open(cwd+"/img/hit.png")),
    "miss" : ImageTk.PhotoImage(Image.open(cwd+"/img/miss.png")),
    "fight" : ImageTk.PhotoImage(Image.open(cwd+"/img/fight.png")),
    "success" : ImageTk.PhotoImage(Image.open(cwd+"/img/success.png")),
}

#アイコンを表示する関数
def setIcon(x,y,type):
    """
    x:キャラのx座標
    y:キャラのy座標
    type:アイコンの種類
    """
    # 一回消して再描写
    canvas.delete("icon")
    canvas.create_image(getRealCoord(x , y-1),image = ICON[type],tag="icon",anchor=tk.NW)#キャラの上に表示するので、y座標はy-1されている

#前のタイルが釣り可能ならば釣りアイコンを表示する関数
def setFishingIcon(x,y,d):
    """
    x:キャラのx座標
    y:キャラのy座標
    d:キャラの向き
    """
    global fishFlag
    
    if d == 0:#下向き
        moveX = 0
        moveY = 1
    elif d == 1:#左向き
        moveX = -1
        moveY = 0
    elif d == 2:#右向き
        moveX = 1
        moveY = 0
    elif d == 3:#上向き
        moveX = 0
        moveY = -1
    
    
    # 移動先がマップ範囲内ならば
    if 0 <= y+moveY < len(MAP_DATA) and 0 <= x+moveX < len(MAP_DATA[0]):
        #前のマスが釣り可能ならば
        if FISHING_PERMIT[MAP_DATA[y+moveY][x+moveX]]:
            setIcon(x,y,"fishing")
            print(f"you can fishing @({x+moveX},{y+moveY})")
            fishFlag = True
        else:
            fishFlag = False
    else:
        # 移動先がマップ範囲外
        fishFlag = False


#>>キャラクター>>
CHARA_WIDTH = 64  #キャラの幅
CHARA_HEIGHT = 96 #キャラの高さ

#キャラクターのマップ座標
charaX = 2 
charaY = 2 
charaD = 1  #キャラの向き
flag = "default"
'''
default:通常状態
move:移動中
'''
FRAME_LIST = [0,1,2,1]

moveCount = 0    #移動カウンタ 0から3の4段階

#ゲームの基本となる1ティック時間(ms)
TICK_TIME = 50

#移動方向
moveX = 0
moveY = 0

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


#マップ座標からキャラをどこに配置するか決める関数
#dx,dy:移動中の微小変化 0,1,2,3,4の4段階
def getCharaCoord(x,y,dx=0,dy=0):
    return((x+dx/4)*CHIP_SIZE, (y+dy/4-0.5)*CHIP_SIZE)

#キャラクターを再描写する関数
def setChara(x,y,d,frame):
    global moveX,moveY
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
    canvas.create_image(getCharaCoord(x,y,(frame+1)*moveX,(frame+1)*moveY),image =img ,tag="chara",anchor=tk.NW)


#>>ゲームのメインループ関数>>
def gameLoop():
    global charaX,charaY,charaD,moveCount,moveX,moveY,flag,key,currentKey,prevKey
    
    if len(key)> 0:
        lastKey = key[len(key) - 1] #最後に押されたキー
    else:
        lastKey = ""
    
    
    if flag == "default": #待機中のとき 

        
        if len(key): #SHIFT以外の何かのキーが押されているとき
            if lastKey=="s" or lastKey=="Down":#下入力
                flag = "move"
                charaD = 0
                moveX = 0
                moveY = 1
                print("↓")
            elif lastKey=="a" or lastKey=="Left":#左入力
                flag = "move"
                charaD = 1
                moveX = -1
                moveY = 0
                print("←")
            elif lastKey=="d" or lastKey=="Right":#右入力
                flag = "move"
                charaD = 2
                moveX = 1
                moveY = 0
                print("→")
            elif lastKey=="w" or lastKey=="Up":#上入力
                flag = "move"
                charaD = 3
                moveX = 0
                moveY = -1
                print("↑")
            
            #上の処理で移動中フラグが立ったとき
            if flag == "move":
                canvas.delete("icon")
                #移動先が通行可能でないならば
                if not PASSAGE_PERMIT[MAP_DATA[charaY+moveY][charaX+moveX]]:
                    #移動をやめて向きのみ変える
                    flag = "default"
                    moveX = 0
                    moveY = 0
                    setChara(charaX,charaY,charaD,1)
                    setFishingIcon(charaX,charaY,charaD)
    
    if flag == "move":#移動中のとき
        #キャラクター再描写
        setChara(charaX,charaY,charaD,moveCount)
        
        if moveCount==3:#アニメーションが最終コマならば
            flag = "default"#待機中に状態を戻す
            moveCount = 0
            charaX += moveX
            charaY += moveY
            setFishingIcon(charaX,charaY,charaD)
        else:
            moveCount += 1
    
    prevKey = copy.deepcopy(key)
    key = copy.deepcopy(currentKey)
    root.after(TICK_TIME,gameLoop)

#>>キー監視>>
currentKey = []#現在押されているキー
key = []       #前回の処理から押されたキー
prevKey = [] #前回の処理までに押されたキー

#何かのキーが押されたときに呼び出される関数
def press(e):
    keysym = e.keysym
    if keysym not in currentKey:#始めて押されたならば
        currentKey.append(keysym)
        print(f"pressed:{keysym}")
    if keysym not in key:#前回の処理から始めて押されたならば
        key.append(keysym)

#何かのキーが離されたときに呼び出される関数
def release(e):
    keysym = e.keysym
    currentKey.remove(keysym)
    print(f"released:{keysym}")

#キー入力をトリガーに関数を呼び出すよう設定する
root.bind("<KeyPress>", press)
root.bind("<KeyRelease>", release)

#>>メインループ>>>
mapping()
canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP[0][1],tag="chara",anchor=tk.NW)

gameLoop()
print("start!")
root.mainloop()