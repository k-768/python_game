import copy
import json
import os
import random
import sys
import numpy
import tkinter as tk
from PIL import Image,ImageTk


#---------------------------------
#Fishing Game for Python learning
#version: 0.92
#last update: 2024/04/23
#latest information:
#・Fixed some bugs
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
root.title("Sample Game ver0.92")
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
def setFishingIcon(x,y,moveX,moveY):
    """
    x:キャラのx座標
    y:キャラのy座標
    moveX:x軸方向の移動
    moveY:y軸方向の移動
    """
    global fishFlag
    # 移動先がマップ範囲内ならば
    if (0 <= y+moveY < len(DEFAULT_MAP)) and (0 <= x+moveX < len(DEFAULT_MAP[0])):
        #前のマスが釣り可能ならば
        if(FISHING_PERMIT[DEFAULT_MAP[y+moveY][x+moveX]]):
            setIcon(x,y,"fishing")
            print(f"you can fishing @({x+moveX},{y+moveY})")
            fishFlag = True
        else:
            fishFlag = False
    else:
        # 移動先がマップ範囲外
        #*マップ間移動をするならここで処理するのが良き*
        fishFlag = False



#>>魚>>
fishFlag = False #釣り可能かどうか

#魚の排出割合
def fishRate(lv):
    return([100-5*lv,4*lv,lv]) 

FISH_IMAGE = {
    "イワシ":tk.PhotoImage(file = cwd+"/img/iwashi.png"),
    "アジ":tk.PhotoImage(file = cwd+"/img/aji.png"),
    "サバ":tk.PhotoImage(file = cwd+"/img/saba.png"),
    "タチウオ":tk.PhotoImage(file = cwd+"/img/tachiuo.png"),
    "カワハギ":tk.PhotoImage(file = cwd+"/img/kawahagi.png"),
    "メバル":tk.PhotoImage(file = cwd+"/img/mebaru.png"),
    "タイ":tk.PhotoImage(file = cwd+"/img/iwashi.png"),
    "スズキ":tk.PhotoImage(file = cwd+"/img/iwashi.png"),
    "カサゴ":tk.PhotoImage(file = cwd+"/img/iwashi.png"),
}
BIG_FISH_IMAGE = {key :img.zoom(2,2) for key , img in FISH_IMAGE.items()}

LOW_RARE_FISH = [
        {
        "name":"イワシ",
        "img":FISH_IMAGE["イワシ"],
        "aveWeight":0.12, #平均重量
        "stDev":0.02, #標準偏差(最大、最小重量≒aveWeight±stDev*2)
        "price":60 #kg単価
        },
        {
        "name":"アジ",
        "img":FISH_IMAGE["アジ"],
        "aveWeight":0.17,
        "stDev":0.04, 
        "price":100
        },
        {
        "name":"サバ",
        "img":FISH_IMAGE["サバ"],
        "aveWeight":0.35,
        "stDev":0.13, 
        "price":50
        },
    ]
MIDDLE_RARE_FISH = [
        {
        "name":"タチウオ",
        "img":FISH_IMAGE["タチウオ"],
        "aveWeight":3,
        "stDev":1, 
        "price":12
        },
        {
        "name":"カワハギ",
        "img":FISH_IMAGE["カワハギ"],
        "aveWeight":0.4,
        "stDev":0.1, 
        "price":80
        },
        {
        "name":"メバル",
        "img":FISH_IMAGE["メバル"],
        "aveWeight":0.43,
        "stDev":0.14, 
        "price":100
        },
    ]
HIGH_RARE_FISH = [
        {
        "name":"タイ",
        "img":FISH_IMAGE["タイ"],
        "aveWeight":5.4,
        "stDev":2.3, 
        "price":20
        },
        {
        "name":"スズキ",
        "img":FISH_IMAGE["スズキ"],
        "aveWeight":5.5,
        "stDev":2.25, 
        "price":19
        },
        {
        "name":"カサゴ",
        "img":FISH_IMAGE["カサゴ"],
        "aveWeight":1.65,
        "stDev":0.58, 
        "price":65
        },
    ]
FISH_LIST = []
FISH_LIST.append(LOW_RARE_FISH)
FISH_LIST.append(MIDDLE_RARE_FISH)
FISH_LIST.append(HIGH_RARE_FISH)


#>>セーブデータ>>
try:
    with open(cwd + "/save/savedata.json") as f:
        saveData = json.load(f)
    print(saveData)
except:
    saveData =  {
        "イワシ":{
            "count":0,            #釣れた回数
            "maxWeight":0,  #最大重量
            "bronze":False,    #bronzeランクを釣ったか
            "silver":False,      #silverランクを釣ったか
            "gold":False,       #goldランクを釣ったか
            "totalWeight":0 #合計重量
        },
        "アジ":{
            "count":0,
            "maxWeight":0, 
            "bronze":False,
            "silver":False, 
            "gold":False,
            "totalWeight":0
        },
        "サバ":{
            "count":0,
            "maxWeight":0, 
            "bronze":False,
            "silver":False, 
            "gold":False,
            "totalWeight":0
        },
        "タチウオ":{
            "count":0,
            "maxWeight":0, 
            "bronze":False,
            "silver":False, 
            "gold":False,
            "totalWeight":0
        },
        "カワハギ":{
            "count":0,
            "maxWeight":0, 
            "bronze":False,
            "silver":False, 
            "gold":False,
            "totalWeight":0
        },
        "メバル":{
            "count":0,
            "maxWeight":0, 
            "bronze":False,
            "silver":False, 
            "gold":False,
            "totalWeight":0
        },
        "タイ":{
            "count":0,
            "maxWeight":0, 
            "bronze":False,
            "silver":False, 
            "gold":False,
            "totalWeight":0
        },
        "スズキ":{
            "count":0,
            "maxWeight":0, 
            "bronze":False,
            "silver":False, 
            "gold":False,
            "totalWeight":0
        },
        "カサゴ":{
            "count":0,
            "maxWeight":0, 
            "bronze":False,
            "silver":False, 
            "gold":False,
            "totalWeight":0
        },
        "money":0,
        "x":3,
        "y":3,
        "d":0,
        "lv":0
    }

#ゲームの情報をjsonファイルにセーブする関数
def saveGame():
    saveData["x"] = charaX
    saveData["y"] = charaY
    saveData["d"] = charaD 
    with open(cwd + "/save/savedata.json",'w') as f:
        json.dump(saveData,f,indent=2)

def lvUp():
    global saveData
    if(saveData["lv"] <= 10):
        if(saveData["money"] >= 30+30*saveData["lv"]):
            saveData["money"] -= 30+30*saveData["lv"]
            saveData["lv"] += 1
            print("Lv."+str(saveData["lv"])+"に上がった")
            money.set(str(saveData["money"])+"G")
            lv.set("Lv, "+ str(saveData["lv"]))
            saveGame()

# >>釣り結果表示>>
RESULT_X = 300
RESULT_Y = 200
RESULT_SIZE = f"{RESULT_X}x{RESULT_Y}+{int((CANVAS_WIDTH - RESULT_X)/2)}+{int((CANVAS_HEIGHT - RESULT_Y)/2)}"


def showResultWindow(fish,rank,weight,price):
    global resultWindow,saveData,FISH_IMAGE
    #ウィンドウ設置
    resultWindow = tk.Toplevel()
    resultWindow.title("Result")
    resultWindow.geometry(RESULT_SIZE)
    resultWindow.resizable(False,False)
    resultWindow.configure(bg="burlywood")
    
    
    # フレームの作成と設置
    nameFrame = tk.Frame(resultWindow , relief=tk.RAISED , bg="burlywood")
    canvasFrame = tk.Frame(resultWindow , relief=tk.RAISED , bg="burlywood")
    infoFrame = tk.Frame(resultWindow , relief=tk.RAISED , bg="burlywood")
    nameFrame.pack(fill = tk.BOTH, pady=10)
    canvasFrame.pack(fill = tk.BOTH, pady=0)
    infoFrame.pack(fill = tk.BOTH, pady=10)
    
    if(rank == "silver"):
        name = "大物の"+fish
        color = "LightBlue4"
    elif(rank == "gold"):
        name = "超大物の"+fish
        color = "gold"
    else:
        name = fish
        color = "DarkOrange4"
    
    viewCanvas = tk.Canvas(canvasFrame,width = 96,height = 48,bg = "burlywood",highlightthickness=0)
    viewCanvas.pack()
    viewCanvas.create_image(48,24,image =BIG_FISH_IMAGE[fish],tag="view",anchor=tk.CENTER)
    
    # 各種ウィジェットの作成
    fishName = tk.Label(nameFrame, text=name, font=("MSゴシック", "20", "bold"),fg = color,bg = "burlywood")
    record = tk.Label(nameFrame, text="Record!!", font=("MSゴシック", "16"),fg = "red3",bg = "burlywood")
    fishWeight = tk.Label(infoFrame, text=str(weight)+" kg", font=("MSゴシック", "16"),bg = "burlywood")
    fishPrice = tk.Label(infoFrame, text=str(price)+" G", font=("MSゴシック", "16"),bg = "burlywood")
    fishName.pack()
    fishWeight.pack()
    fishPrice.pack()
    if(weight == saveData[fish]["maxWeight"]):
        record.pack()

#>>キャラクター>>
CHARA_WIDTH = 64  #キャラの幅
CHARA_HEIGHT = 96 #キャラの高さ

#キャラクターのマップ座標
charaX = saveData["x"] 
charaY = saveData["y"] 
charaD = saveData["d"]  #キャラの向き
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

#キャラクターを再描写する関数
def setChara(x,y,d,frame,source = "walk"):
    """
    x:キャラのX座標
    y:キャラのY座標
    d:キャラの向き
    frame:コマ数
    source:"walk" or "fishing"
    """
    #キャラの画像を選択
    if source == "walk":
        img = CHARA_CHIP[d][frame]
    else:
        img = CHARA_CHIP_WAIT[d][frame]
    
    #今の画像を消して再描写
    canvas.delete("chara")
    canvas.create_image(getCharaCoord(x,y),image =img ,tag="chara",anchor=tk.NW)

#>>釣り竿>>
ROD_WIDTH = 128
ROD_HEIGHT  = 160
ROD_SHEET = Image.open(cwd+"/img/rod.png")
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
        dx = random.randint(0,2) -1 #-1,0,1のいずれか
        dy = random.randint(0,2) -1
    
    return((x)*CHIP_SIZE_X + dx, (y-0.5)*CHIP_SIZE_Y +dy)

#釣り竿を描写する関数
def setLod(x,y,d,frame):
    #釣り竿を削除して再描写
    canvas.delete("rod")
    canvas.create_image(getRodCoord(x,y,d),image = ROD[d][frame],tag="rod",anchor=tk.NW)


#>>ゲームのメインループ関数>>
def gameLoop():
    global charaX,charaY,charaD,saveData,dashFlag,moveCount,moveX,moveY,flag,key,currentKey,prevKey,speed,waitTick,fishingCount,resultWindow
    
    lastKey = len(key) - 1 #最後に押されたキーの配列番号
    speed = 1
    
    #Ctrl+Cが押されたとき、セーブして終了
    if(key.count("Control_L") and key.count("c")):
        saveGame()
        sys.exit()
    
    if (flag == "defalt"): #待機中のとき 
        if(fishFlag):#魚釣り可能な場所でSpaceが押されたら釣り開始
            if(key.count("space") and (not prevKey.count("space"))):
                canvas.delete("icon")#釣りアイコン削除
                flag = "wait"
                waitTick = random.randint(round(3000/TICK_TIME),round(5000/TICK_TIME))#3-5秒
                fishingCount = 0
        
        if(key.count("Shift_L")):#Shiftキーが押されているならダッシュ
            dashFlag = True
            if(key.index("Shift_L") == lastKey):
                lastKey -= 1
        else:
            dashFlag = False
        
        if(len(key)): #SHIFT以外の何かのキーが押されているとき
            if(key[lastKey]=="s" or key[lastKey]=="Down"):#下入力
                flag = "move"
                charaD = 0
                moveX = 0
                moveY = 1
                print("↓")
            elif(key[lastKey]=="a" or key[lastKey]=="Left"):#左入力
                flag = "move"
                charaD = 1
                moveX = -1
                moveY = 0
                print("←")
            elif(key[lastKey]=="d" or key[lastKey]=="Right"):#右入力
                flag = "move"
                charaD = 2
                moveX = 1
                moveY = 0
                print("→")
            elif(key[lastKey]=="w" or key[lastKey]=="Up"):#上入力
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
                    setChara(charaX,charaY,charaD,1,"walk")
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
            setChara(charaX,charaY,charaD,1,"fishing")
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
        
        # スペースキーが再び押された時
        if(key.count("space") and not prevKey.count("space") and  fishingCount): 
            setChara(charaX,charaY,charaD,1,"walk")
            canvas.delete("rod")
            setIcon(charaX,charaY,"miss")#アイコン描写
            print("早すぎた！")
            flag = "defalt"
            
        if (flag == "wait"):
            fishingCount += 1
    
    elif (flag == "bite"): #魚が少し喰いついたとき
        if(key.count("space")):  #スペースキー押下されたとき
            #釣りの姿勢から歩行姿勢に戻す
            setChara(charaX,charaY,charaD,1,"walk")
            canvas.delete("rod")
            setIcon(charaX,charaY,"miss")#アイコン描写
            print("早すぎた！")
            flag = "defalt"
        elif(fishingCount == 0):#初回なら
            #キャラクター再描写
            setChara(charaX,charaY,charaD,1,"fishing")
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
        if(key.count("space")):  #スペースキー押下されたとき
            flag = "fight"
            setIcon(charaX,charaY,"fight")#アイコン描写
            fishingCount = 0
        elif(fishingCount == 0):#初回なら
            #キャラクター再描写
            setChara(charaX,charaY,charaD,2,"fishing")
            #釣り竿再描写
            canvas.delete("rod")
            canvas.create_image(getRodCoord(charaX,charaY,charaD),image = ROD[charaD][2],tag="rod",anchor=tk.NW)
            setIcon(charaX,charaY,"hit")#アイコン描写
            print("ビク！")
        elif(fishingCount == waitTick):#待ち時間を終えたとき
            print("遅すぎた！")
            #釣りの姿勢から歩行姿勢に戻す
            setChara(charaX,charaY,charaD,1,"walk")
            canvas.delete("rod")
            setIcon(charaX,charaY,"miss")#アイコン描写
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
        selectedFish = random.choice((random.choices(FISH_LIST,k=1,weights = fishRate(saveData["lv"])))[0])
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
        
        #データを更新する
        saveData[selectedFish["name"]]["count"] += 1 #釣った数+1
        saveData[selectedFish["name"]]["totalWeight"] += fishWeight #総重量加算
        
        if(not saveData[selectedFish["name"]][fishRank] ): #そのランクを釣るのが初めてなら更新
            saveData[selectedFish["name"]][fishRank] = True
            
        if(saveData[selectedFish["name"]]["maxWeight"] < fishWeight ): #釣った魚が今までで一番重ければ記録を更新
            saveData[selectedFish["name"]]["maxWeight"] = fishWeight
        
        saveData["money"] += fishPrice #所持金を更新
        saveGame()
        print(saveData["money"])
        money.set(str(saveData["money"])+"G")
        
        #釣りの姿勢から通常状態に戻す
        setChara(charaX,charaY,charaD,1,"walk")
        canvas.delete("rod")
        #*魚を仮表示
        canvas.delete("fish")
        canvas.create_image(getCharaCoord(charaX+0.5,charaY+1),image = selectedFish["img"],tag="fish",anchor=tk.CENTER)
        setIcon(charaX,charaY,"success")#アイコン描写
        showResultWindow(selectedFish["name"],fishRank,fishWeight,fishPrice)
        lvUp()
        flag = "result"
        
    elif(flag == "result"): #結果表示中のとき
        if(key.count("space")):  #スペースキー押下されたとき
            flag = "defalt"
            canvas.delete("fish")
            setFishingIcon(charaX,charaY,moveX,moveY)
            resultWindow.destroy()
    
    prevKey = copy.deepcopy(key)
    key = copy.deepcopy(currentKey)
    root.after(round(TICK_TIME/speed),gameLoop)

#所持金が変更されたとき呼び出され、表示を変更する
def onMoneyChange(varname, index, mode):
    canvas.itemconfigure(money_text, text=root.getvar(varname))

def onLvChange(varname, index, mode):
    canvas.itemconfigure(lv_text, text=root.getvar(varname))

#>>キー監視>>
currentKey = []#現在押されているキー
key = []       #前回の処理から押されたキー
prevKey = [] #前回の処理までに押されたキー

#何かのキーが押されたときに呼び出される関数
def press(e):
    keysym = e.keysym
    if(not currentKey.count(keysym)):#始めて押されたならば
        currentKey.append(keysym)
        print(f"pressed:{keysym}")
    if(not key.count(keysym)):#前回の処理から始めて押されたならば
        key.append(keysym)

#何かのキーが離されたときに呼び出される関数
def release(e):
    keysym = e.keysym
    currentKey.remove(keysym)
    print(f"released:{e.keysym}")

#キー入力をトリガーに関数を呼び出すよう設定する
root.bind("<KeyPress>", press)
root.bind("<KeyRelease>", release)

#>>メインループ>>>
mapping()
canvas.create_image(getCharaCoord(charaX,charaY),image = CHARA_CHIP[0][1],tag="chara",anchor=tk.NW)

#>>情報表示
lv = tk.StringVar(root,"Lv. "+str(saveData["lv"]))
lv.trace_add('write', onLvChange)
lv_text = canvas.create_text(CHIP_SIZE_X*(X_MAPSIZE-1),30, fill = "brown",font = ("System",24), text = lv.get(), tag = "lv")
money = tk.StringVar(root,str(saveData["money"])+"G")
money.trace_add('write', onMoneyChange)
money_text = canvas.create_text(CHIP_SIZE_X*(X_MAPSIZE-1),80, fill = "brown",font = ("System",24), text = money.get(), tag = "money")

gameLoop()
print("start!")
root.mainloop()