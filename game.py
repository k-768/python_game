import copy
import os
import random
import numpy
import tkinter as tk
from PIL import Image,ImageTk


#---------------------------------
#Fishing Game for Python learning
#version: 0.73
#last update: 2024/04/20
#latest information:
#・Set rank by size
#・Added images of fish up to medium rare
#author: k-768
#---------------------------------

#>>ディレクトリ>>
cwd = os.getcwd()


#>>マップ設定>>
CHIP_SIZE_X = 64  #チップのxピクセル数
CHIP_SIZE_Y = 64  #チップのyピクセル数
X_MAPSIZE = 20    #マップのx方向タイル数
Y_MAPSIZE = 10    #マップのy方向タイル数


#>>ウィンドウ、キャンバス>>
CANVAS_WIDTH = CHIP_SIZE_X * X_MAPSIZE #キャンバス幅
CANVAS_HEIGHT = CHIP_SIZE_Y * Y_MAPSIZE #キャンバス高さ
MARGINE_X = 2 #マージン
MARGINE_Y = 2 #マージン
CANVAS_SIZE = f"{CANVAS_WIDTH+MARGINE_X}x{CANVAS_HEIGHT+MARGINE_Y}"#キャンバスサイズ

#ウィンドウ設置
root = tk.Tk()
root.title("Sample Game ver0.73")
root.geometry(CANVAS_SIZE)

#キャンバス設置
canvas = tk.Canvas(root,width = CANVAS_WIDTH,height = CANVAS_HEIGHT,bg = "skyblue")
canvas.pack()


#>>マップチップ>>
#マップチップを1枚の画像に並べたマップシートを読み込む
MAP_SHEET = Image.open(cwd+"/img/sheet1.png")

#読み込んだ画像から縦横何枚ずつチップがあるか求める
CHIP_X = MAP_SHEET.width // CHIP_SIZE_X
CHIP_Y = MAP_SHEET.height // CHIP_SIZE_Y

#マップシートをマップチップに分割し配列に格納する
MAP_CHIP = [
    ImageTk.PhotoImage(MAP_SHEET.crop((
        CHIP_SIZE_X*(i%CHIP_X) , 
        CHIP_SIZE_Y*(i//CHIP_X) , 
        CHIP_SIZE_X*(i%CHIP_X+1) , 
        CHIP_SIZE_Y*((i//CHIP_X)+1)
        ))) for i in range(CHIP_X*CHIP_Y)
    ]

#>>マップデータ>>
#
DEFAULT_MAP = [
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
            #1回消して再描画
            canvas.delete(f"chip{x},{y}")
            canvas.create_image(
                getRealCoord(x, y),
                image = MAP_CHIP[DEFAULT_MAP[y][x]],
                tag=f"chip{x},{y}",
                anchor=tk.NW
                )
    print("map setting is done")

#マップ座標から画面座標に変換
def getRealCoord(mapx, mapy):
    return(mapx * CHIP_SIZE_X, mapy * CHIP_SIZE_Y)


#>>釣りアイコン>>
FISHING_ICON = ImageTk.PhotoImage(Image.open(cwd+"/img/fishing.png"))
HIT_ICON = ImageTk.PhotoImage(Image.open(cwd+"/img/hit.png"))

#前のタイルが釣り可能ならば釣りアイコンを表示する関数
def setFishingIcon(charaX,charaY,moveX,moveY):
    """
    charaX:キャラのx座標
    charaY:キャラのy座標
    moveX:x軸方向の移動
    charaX:y軸方向の移動
    """
    global fishFlag
    if (0 <= charaY+moveY < len(DEFAULT_MAP)) and (0 <= charaX+moveX < len(DEFAULT_MAP[0])):
        # 移動先がマップ範囲内
        if(FISHING_PERMIT[DEFAULT_MAP[charaY+moveY][charaX+moveX]]):
            #前のマスが釣り可能
            canvas.create_image(
                getRealCoord(charaX,charaY-1),
                image = FISHING_ICON,
                tag="icon",anchor=tk.NW
                )
            print(f"you can fishing @({charaX+moveX},{charaY+moveY})")
            fishFlag = True
        else:
            fishFlag = False
    else:
        # 移動先がマップ範囲外
        #*マップ間移動をするならここで処理するのが良き*
        fishFlag = False



#>>魚>>
fishFlag = False #釣り可能かどうか
FISH_RATE = [70,25,5] #魚の排出割合
LOW_RARE_FISH = [
        {
        "name":"イワシ",
        "img":ImageTk.PhotoImage(Image.open(cwd+"/img/iwashi.png")),
        "aveWeight":0.12, #平均重量
        "stDev":0.02, #標準偏差(最大、最小重量≒aveWeight±stDev*2)
        "price":60 #kg単価
        },
        {
        "name":"アジ",
        "img":ImageTk.PhotoImage(Image.open(cwd+"/img/aji.png")),
        "aveWeight":0.17,
        "stDev":0.04, 
        "price":100
        },
        {
        "name":"サバ",
        "img":ImageTk.PhotoImage(Image.open(cwd+"/img/saba.png")),
        "aveWeight":0.35,
        "stDev":0.13, 
        "price":50
        },
    ]
MIDDLE_RARE_FISH = [
        {
        "name":"タチウオ",
        "img":ImageTk.PhotoImage(Image.open(cwd+"/img/tachiuo.png")),
        "aveWeight":3,
        "stDev":1, 
        "price":12
        },
        {
        "name":"カワハギ",
        "img":ImageTk.PhotoImage(Image.open(cwd+"/img/kawahagi.png")),
        "aveWeight":0.4,
        "stDev":0.1, 
        "price":80
        },
        {
        "name":"メバル",
        "img":ImageTk.PhotoImage(Image.open(cwd+"/img/mebaru.png")),
        "aveWeight":0.43,
        "stDev":0.14, 
        "price":100
        },
    ]
HIGH_RARE_FISH = [
        {
        "name":"タイ",
        "img":ImageTk.PhotoImage(Image.open(cwd+"/img/aji.png")),
        "aveWeight":5.4,
        "stDev":2.3, 
        "price":20
        },
        {
        "name":"スズキ",
        "img":ImageTk.PhotoImage(Image.open(cwd+"/img/aji.png")),
        "aveWeight":5.5,
        "stDev":2.25, 
        "price":19
        },
        {
        "name":"カサゴ",
        "img":ImageTk.PhotoImage(Image.open(cwd+"/img/aji.png")),
        "aveWeight":1.65,
        "stDev":0.58, 
        "price":65
        },
    ]
FISH_LIST = []
FISH_LIST.append(LOW_RARE_FISH)
FISH_LIST.append(MIDDLE_RARE_FISH)
FISH_LIST.append(HIGH_RARE_FISH)

fishLog =  [
        {
        "name":"イワシ",
        "count":0,            #釣れた回数
        "maxWeight":0,  #最大重量
        "silver":False,      #silverランクを釣ったか
        "gold":False,       #goldランクを釣ったか
        "totalWeight":0 #合計重量
        },
        {
        "name":"アジ",
        "count":0,
        "maxWeight":0, 
        "silver":False, 
        "gold":False,
        "totalWeight":0
        },
        {
        "name":"サバ",
        "count":0,
        "maxWeight":0, 
        "silver":False, 
        "gold":False,
        "totalWeight":0
        },
        {
        "name":"タチウオ",
        "count":0,
        "maxWeight":0, 
        "silver":False, 
        "gold":False,
        "totalWeight":0
        },
        {
        "name":"カワハギ",
        "count":0,
        "maxWeight":0, 
        "silver":False, 
        "gold":False,
        "totalWeight":0
        },
        {
        "name":"メバル",
        "count":0,
        "maxWeight":0, 
        "silver":False, 
        "gold":False,
        "totalWeight":0
        },
        {
        "name":"タイ",
        "count":0,
        "maxWeight":0, 
        "silver":False, 
        "gold":False,
        "totalWeight":0
        },
        {
        "name":"スズキ",
        "count":0,
        "maxWeight":0, 
        "silver":False, 
        "gold":False,
        "totalWeight":0
        },
        {
        "name":"カサゴ",
        "count":0,
        "maxWeight":0, 
        "silver":False, 
        "gold":False,
        "totalWeight":0
        },
    ]

#>>キャラクター>>
CHARA_WIDTH = 64  #キャラの幅
CHARA_HEIGHT = 96 #キャラの高さ

#キャラクターのマップ座標
charaX = 3 
charaY = 3
charaD = 0 #キャラの向き
money = 0 #所持金
flag = "defalt"
'''
defalt:通常状態
move:移動中
wait:釣り中
bite:ウキがピクつく
hit:ウキが沈む
fight:格闘中
success:釣り成功
miss:釣り失敗
result:釣り結果表示
'''
fishingCount = 0
waitTick = 0

dashFlag = False #ダッシュするか
moveCount = 0    #移動カウンタ 0から3の4段階

#ゲームの基本となる1ティック時間(ms)
TICK_TIME = 50
speed = 0.5 #ゲームの進行速度  

#移動方向
moveX = 0
moveY = 0

#キャラチップを1毎の画像に並べたキャラシートを読み込む
CHARA_SHEET = Image.open(cwd+"/img/character.png")
CHARA_SHEET_WAIT = Image.open(cwd+"/img/character_wait.png")

#読み込んだ画像から縦横何枚ずつチップがあるか求める
CHARA_X = CHARA_SHEET.width // CHARA_WIDTH
CHARA_Y = CHARA_SHEET.height // CHARA_HEIGHT

#キャラチップに分割し2次元配列に格納する
CHARA_CHIP = [
    [
        ImageTk.PhotoImage(CHARA_SHEET.crop((
            CHARA_WIDTH * i,
            CHARA_HEIGHT * j,
            CHARA_WIDTH * (i + 1),
            CHARA_HEIGHT * (j + 1)
            ))) for i in range(CHARA_X)
        ]for j in range(CHARA_Y)
    ]

CHARA_CHIP_WAIT = [
    [
        ImageTk.PhotoImage(CHARA_SHEET_WAIT.crop((
            CHARA_WIDTH * i,
            CHARA_HEIGHT * j,
            CHARA_WIDTH * (i + 1),
            CHARA_HEIGHT * (j + 1)
            ))) for i in range(CHARA_X)
        ]for j in range(CHARA_Y)
    ]

#マップ座標からキャラをどこに配置するか決める関数
#dx,dy:移動中の微小変化 0,0.25,0.5,0.75,1の5段階
def getCharaCoord(x,y,dx=0,dy=0):
    return((x+dx)*CHIP_SIZE_X, (y+dy-0.5)*CHIP_SIZE_Y)

#>>釣り竿>>
ROD_WIDTH = 128
ROD_HEIGHT  = 160
ROD_SHEET = CHARA_SHEET = Image.open(cwd+"/img/rod.png")
ROD = [
    [
        ImageTk.PhotoImage(ROD_SHEET.crop((
            ROD_WIDTH * i,
            ROD_HEIGHT * j,
            ROD_WIDTH * (i + 1),
            ROD_HEIGHT * (j + 1)
            ))) for i in range(CHARA_X)
        ]for j in range(CHARA_Y)
    ]

#マップ座標から釣り竿をどこに配置するか決める関数
def getRodCoord(x,y,d,isRandom = False):
    dx = 0
    dy = 0
    
    if(d==1):
        x -= 1
    elif(d==3):
        y -= 1
    
    if(isRandom):
        dx = random.randint(0,2) -1
        dy = random.randint(0,2) -1
    
    return((x)*CHIP_SIZE_X + dx, (y-0.5)*CHIP_SIZE_Y +dy)

#ゲームのメインループ関数
def gameLoop():
    global charaX,charaY,charaD,money,dashFlag,moveCount,moveX,moveY,flag,key,currentKey,prevKey,speed,waitTick,fishingCount
    
    lastKey = len(key) - 1 #最後に押されたキーの配列番号
    speed = 1
    if (flag == "defalt"): #待機中のとき 
        if(fishFlag):#魚釣り可能な場所でSpaceが押されたら釣り開始
            if(key.count(32) and (not prevKey.count(32))):
                canvas.delete("icon")#釣りアイコン削除
                flag = "wait"
                waitTick = random.randint(round(3000/TICK_TIME),round(5000/TICK_TIME))#3-5秒

                fishingCount = 0
        
        if(key.count(16)):#Shiftキーが押されているならダッシュ
            dashFlag = True
            if(key.index(16) == lastKey):
                lastKey -= 1
        else:
            dashFlag = False
        
        if(len(key)): #SHIFT以外の何かのキーが押されているとき
            if(key[lastKey]==40 or key[lastKey]==83):#下入力
                flag = "move"
                charaD = 0
                moveX = 0
                moveY = 1
                print("↓")
            elif(key[lastKey]==37 or key[lastKey]==65):#左入力
                flag = "move"
                charaD = 1
                moveX = -1
                moveY = 0
                print("←")
            elif(key[lastKey]==39 or key[lastKey]==68):#右入力
                flag = "move"
                charaD = 2
                moveX = 1
                moveY = 0
                print("→")
            elif(key[lastKey]==38 or key[lastKey]==87):#上入力
                flag = "move"
                charaD = 3
                moveX = 0
                moveY = -1
                print("↑")
            
            #上の処理で移動中フラグが立ったとき
            if(flag == "move"):
                canvas.delete("icon")#釣りアイコン削除
                #移動先が通行可能でないならば
                if(not PASSAGE_PERMIT[DEFAULT_MAP[charaY+moveY][charaX+moveX]]):
                    #移動をやめて向きのみ変える
                    flag = "defalt"
                    canvas.delete("chara")
                    canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP[charaD][1],tag="chara",anchor=tk.NW)
                    setFishingIcon(charaX,charaY,moveX,moveY)
    
    if (flag == "move"):#移動中のとき
        #キャラクター再描写
        canvas.delete("chara")
        canvas.create_image(getCharaCoord(charaX,charaY,(moveCount+1)*moveX*0.25,(moveCount+1)*moveY*0.25),image = CHARA_CHIP[charaD][moveCount-2*(moveCount//3)],tag="chara",anchor=tk.NW)
        if(dashFlag):
            speed = 1
        else:
            speed = 0.5
        
        if(moveCount==3):#アニメーションが最終コマならば
            flag = "defalt"#待機中に状態を戻す
            dashFlag = False
            moveCount = 0
            charaX += moveX
            charaY += moveY
            setFishingIcon(charaX,charaY,moveX,moveY)
        else:
            moveCount += 1
    
    elif (flag == "wait"):#魚釣り中のとき
        if(fishingCount == 0):#初回なら
            #キャラクター再描写
            canvas.delete("chara")
            canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP_WAIT[charaD][1],tag="chara",anchor=tk.NW)
            #釣り竿描写
            canvas.delete("rod")
            canvas.create_image(getRodCoord(charaX,charaY,charaD),image = ROD[charaD][1],tag="rod",anchor=tk.NW)
        elif(fishingCount >= waitTick):#待ち時間を終えたとき
            if(random.randint(1,3)==1):#1/3の確率で
                flag = "hit"
                waitTick = 10
                fishingCount = 0
            else:
                flag = "bite"
                waitTick = random.randint(2,10)
                fishingCount = 0
        
        if(key.count(32) and not prevKey.count(32) and  fishingCount):  #スペースキー押下されたとき
            canvas.delete("chara")
            canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP[charaD][1],tag="chara",anchor=tk.NW)
            canvas.delete("rod")
            print("早すぎた！")
            flag = "defalt"
            
        if (flag == "wait"):
            fishingCount += 1
    
    elif (flag == "bite"): #魚が少し喰いついたとき
        if(key.count(32)):  #スペースキー押下されたとき
            canvas.delete("chara")
            canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP[charaD][1],tag="chara",anchor=tk.NW)
            canvas.delete("rod")
            print("早すぎた！")
            flag = "defalt"
        elif(fishingCount == 0):#初回なら
            #キャラクター再描写
            canvas.delete("chara")
            canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP_WAIT[charaD][1],tag="chara",anchor=tk.NW)
            #釣り竿再描写
            canvas.delete("rod")
            canvas.create_image(getRodCoord(charaX,charaY,charaD),image = ROD[charaD][0],tag="rod",anchor=tk.NW)
            print("ピク...")
        elif(fishingCount == waitTick):#待ち時間を終えたとき
            flag = "wait"
            waitTick = random.randint(round(200/TICK_TIME),round(2000/TICK_TIME))
            fishingCount = 0
        
        if (flag == "bite"):
            fishingCount += 1
    
    elif (flag == "hit"): #魚がかかったとき
        if(key.count(32)):  #スペースキー押下されたとき
            flag = "fight"
            fishingCount = 0
        elif(fishingCount == 0):#初回なら
            #キャラクター再描写
            canvas.delete("chara")
            canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP_WAIT[charaD][2],tag="chara",anchor=tk.NW)
            #釣り竿再描写
            canvas.delete("rod")
            canvas.create_image(getRodCoord(charaX,charaY,charaD),image = ROD[charaD][2],tag="rod",anchor=tk.NW)
            #アイコン描写
            canvas.create_image(getRealCoord(charaX,charaY-1),image = HIT_ICON,tag="icon",anchor=tk.NW)
            print("ビク！")
        elif(fishingCount == waitTick):#待ち時間を終えたとき
            print("早すぎた！")
            canvas.delete("chara")
            canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP[charaD][1],tag="chara",anchor=tk.NW)
            canvas.delete("rod")
            flag = "defalt"
        
        if (flag == "hit"):
            fishingCount += 1
    
    elif (flag == "fight"): #かかった魚を釣り上げているとき
        if(fishingCount < 20):
            speed = 0.5
            canvas.delete("rod")
            canvas.create_image(getRodCoord(charaX,charaY,charaD,True),image = ROD[charaD][2],tag="rod",anchor=tk.NW)
            fishingCount += 1
        else:
            flag = "success"
    
    elif(flag == "success"): #釣りに成功したとき
        #ランダムな魚を選択
        selectedFish = random.choice((random.choices(FISH_LIST,k=1,weights = FISH_RATE))[0])
        print(selectedFish["name"])
        #魚の重さを決定(正規分布に従う)
        rng = numpy.random.default_rng()
        fishWeight = rng.normal(selectedFish["aveWeight"],selectedFish["stDev"])
        fishWeight = round(fishWeight,2) #少数第3位で四捨五入
        print(fishWeight)
        #重さから売却価格を決定
        fishPrice = fishWeight * selectedFish["price"]
        
        #魚のランクを決定、ランクに応じて価格を上方修正
        if(fishWeight > selectedFish["aveWeight"]+ 2*selectedFish["stDev"]):
            fishRank = "gold"
            fishPrice *= 1.25
            print("🥇")
        elif (fishWeight > selectedFish["aveWeight"]+ 1.5*selectedFish["stDev"]):
            fishRank = "silver"
            fishPrice *= 1.1
            print("🥈")
        else:
            fishRank = "bronze"
        
        fishPrice = round(fishPrice) #四捨五入
        money += fishPrice
        print(fishPrice)
        
        #画像を更新する
        canvas.delete("chara")
        canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP[charaD][1],tag="chara",anchor=tk.NW)
        canvas.delete("rod")
        canvas.delete("icon")
        canvas.delete("fish")
        canvas.create_image(getCharaCoord(charaX,charaY),image = selectedFish["img"],tag="fish",anchor=tk.NW)
        flag = "result"
        
    elif(flag == "result"): #結果表示中のとき
        if(key.count(32)):  #スペースキー押下されたとき
            flag = "defalt"
            canvas.delete("fish")
            setFishingIcon(charaX,charaY,moveX,moveY)
    
    prevKey = copy.deepcopy(key)
    key = copy.deepcopy(currentKey)
    root.after(round(TICK_TIME/speed),gameLoop)


#>>キー監視>>
currentKey = []#現在押されているキー
key = []       #前回の処理から押されたキー
prevKey = [] #前回の処理までに押されたキー

#何かのキーが押されたときに呼び出される関数
def press(e):
    keycode = e.keycode
    if(not currentKey.count(keycode)):#始めて押されたならば
        currentKey.append(keycode)
        print(f"pressed:{e.keysym}")
    if(not key.count(keycode)):#前回の処理から始めて押されたならば
        key.append(keycode)

#何かのキーが離されたときに呼び出される関数
def release(e):
    keycode = e.keycode
    currentKey.remove(keycode)
    print(f"released:{e.keysym}")

#キー入力をトリガーに関数を呼び出すよう設定する
root.bind("<KeyPress>", press)
root.bind("<KeyRelease>", release)

#>>メインループ>>>
mapping()
canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP[0][1],tag="chara",anchor=tk.NW)
gameLoop()
print("start!")
root.mainloop()