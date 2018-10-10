# -*- coding: utf-8 -*-
from time import sleep
import time
import os
import  json
import pprint
import threading
import signal
import sys
from pet_def import *
import datetime

#定数定義
SAMPLING_TIME=0.3           #サンプリングタイム
SERV_REQ='../dat/serv_req.json' #SERVリクエストファイル

#グローバル変数
gthread_serv = ""
gthread_enablefg = True #スレッドの有効フラグ
gserv_start_time = None
gserv_cntrl = ""
gserv_pattern = ""
gserv_time = None

#jsonファイルのパース処理
def parse_req_file(filename) :
    with open(SERV_REQ) as f:
        d = json.load(f)
    pprint.pprint(d, width=40)
    return d

#サーボ駆動 val (0-100%)
def serv_mov(val) :
    com1="echo "
    servonum1=0
    servoang1=servo1range
    com2="% | sudo tee /dev/servoblaster"
    str2=com1+str(servonum1)+"="+str(val)+com2
    os.system(str2)

#Servスレッド
def exec_serv_thread() :
    global gthread_enablefg, gserv_cntrl, gserv_pattern, gserv_time, gserv_color, gserv_start_time
    serv_val_def = 50
    #サーボの値を初期化位置に設定する。
    serv_val = serv_val_def
    serv_dir = 1
    while 1 :
        if gthread_enablefg == False :
            print("end exec_serv_thread")
            return
         
        #停止処理の場合  
        if gserv_cntrl ==  ServCntrl.STOP:
            sleep(SAMPLING_TIME)  
            serv_val = serv_val_def
             continue
 
        #経過時間のチェック
        if gserv_start_time != None and gserv_time > 0:
            now = datetime.datetime.now()  
            diftime = now - gserv_start_time  
            if diftime.total_seconds() > gserv_time :
                sleep(SAMPLING_TIME)
                serv_val = serv_val_def
                continue
 
        #CENTERへの移動
        if gserv_pattern == SERVPattern.CENTER : 
            serv_mov(serv_val_def )
            sleep(2)
            continue

        #SCAN駆動
        if gserv_pattern == SERVPattern.SCAN : 
            #SCANの場合には、サンプリングタイム毎にゆっくり動く
            minval = 40     #サーボ駆動時のmin値
            maxval = 80     #サーボ駆動時のmax値
            serv_div = 3    #サーボ移動の分解能
            serv_sampling_time = 0.5 #スキャン時のサンプリング時間
            serv_val = serv_val*serv_dir*serv_div;
            if serv_val > maxval :
                serv_val = maxval;
                serv_dir = -1
            
            if serv_val < minval :
                serv_val = minval;
                serv_dir = 1

            serv_mov(serv_val )
            sleep(2)
            continue
      
#SERVコントロール情報の更新
def update_serv_cntrl(d): 
    global gserv_cntrl, gserv_pattern, gserv_time

    print("update serv arg=",d)

    #コントロールモードの確認
    if d.get('CNTRL') != None :
         gserv_cntrl = int(d.get('CNTRL'))

    #実行パターンの確認
    if d.get('PATTERN') != None :
         gserv_pattern = int(d.get('PATTERN'))

    #時間の確認
    if d.get('TIME') != None :
        gserv_time = int(d.get('TIME'))
        #Timeが指定されている場合には時間を更新する。
        gserv_start_time =  datetime.datetime.now()    
    else :
        #Timeが設定されていない場合には、開始時間をNoneに設定する。
        gserv_start_time = None
    
    print("update_serv_cntrl. cntrl",gserv_cntrl, "pattern", gserv_pattern, "time", gserv_time)
        
#終了処理
def handler(signal, frame):
    global gthread_led, gthread_enablefg
    gthread_enablefg = False
    gthread_led.join()
    print('exit')
    sys.exit(0)

#サーボの初期化処理
def init_serv() :
    #servの初期化処理
    pathdir=os.path.dirname(os.path.abspath(__file__))
    path1="/PiBits/ServoBlaster/user/servod --p1pins=7 --pcm"
    pathsudo="sudo "
    pathkill="sudo killall servod"

    path=pathsudo+pathdir+path1
    print(path)

    os.system(path)


#mainプログラム
if __name__== '__main__':
    #write json test
    
    """
    d={'PATTERN':1, 'CNTRL':'1', 'TIME':20}
    print(d)
    with open('../dat/serv_req.json', 'w') as f:
        json.dump(d, f, indent=4)
    """
    """    
    print("enum test", LEDCntrl.NONE)
    if LEDCntrl.NONE == 0 :
        print("enum test ok", LEDCntrl.NONE)
    """

    #サーボの初期化処理
    init_serv() 
    
    #シグナルハンドラの登録(Cntrl+Cを受け取った際の終了処理)
    signal.signal(signal.SIGINT, handler)
 
    #Servスレッドの作成と実行
    gthread_serv = threading.Thread(target=exec_serv_thread)
    gthread_serv.start()
    
    #実行ループ(ファイルチェック)
    while 1 :
        #check conf file
        if os.path.exists(SERV_REQ) == True :
            d=parse_req_file(SERV_REQ)
            os.remove(SERV_REQ)
            update_led_cntrl(d)
        
        sleep(SAMPLING_TIME)