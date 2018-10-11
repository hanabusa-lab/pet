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
SERV_IO = 0 #SERVOのGPIO
SERVD_PATH = "/pet/bin/PiBits/ServoBlaster/user/servod"

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
    cmd="echo "+str(SERV_IO)+"="+str(val)+"% | sudo tee /dev/servoblaster"
    os.system(cmd)
    print(datetime.datetime.now() , "serv_mov", cmd)

#Servスレッド
def exec_serv_thread() :
    global gthread_enablefg, gserv_cntrl, gserv_pattern, gserv_time, gserv_start_time
    serv_val_def = 50
    #サーボの値を初期化位置に設定する。
    serv_val = serv_val_def
    serv_dir = 1
    serv_div = 2    #サーボ移動の分解能
    serv_sampling_time = 0.1 #スキャン時のサンプリング時間
            
    while 1 :
        print("thread", gserv_cntrl, gserv_pattern, gserv_start_time, gserv_time)
        if gthread_enablefg == False :
            print("end exec_serv_thread")
            return
         
        #停止処理の場合  
        if gserv_cntrl ==  ServCntrl.STOP:
            #kill serv
            #cmd="sudo killall servod"
            #os.system(cmd)
            sleep(SAMPLING_TIME)
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
        if gserv_pattern == ServPattern.CENTER :             
            if serv_val == serv_val_def :
                sleep(SAMPLING_TIME)
                continue

            if serv_val > serv_val_def :
                serv_dir = -1
            else :
                serv_dir = 1
                
            #serv_valがserv_val_defになるまで、動く
            while True :
                serv_val = serv_val + serv_div*serv_dir
                
                if serv_dir > 0 and serv_val > serv_val_def :
                    serv_val = serv_val_def
                    serv_mov(serv_val )
                    print("moved to center")              
                    break;
        
                if serv_dir < 0 and serv_val < serv_val_def :
                    serv_val = serv_val_def
                    serv_mov(serv_val )
                    print("moved to center")                            
                    break;
                serv_mov(serv_val )
                sleep(serv_sampling_time)
                continue
        
        #SCAN駆動
        if gserv_pattern == ServPattern.SCAN : 
            #SCANの場合には、サンプリングタイム毎にゆっくり動く
            minval = serv_val_def-13     #サーボ駆動時のmin値
            maxval = serv_val_def+13     #サーボ駆動時のmax値
            serv_val = serv_val+serv_dir*serv_div;
            if serv_val > maxval :
                serv_val = maxval;
                serv_dir = -1
            
            if serv_val < minval :
                serv_val = minval;
                serv_dir = 1

            serv_mov(serv_val )
            sleep(serv_sampling_time)
            continue

    print("sleep thread")
    sleep(SAMPLING_TIME)
      
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
    global gthread_serv, gthread_enablefg
    gthread_enablefg = False
    gthread_serv.join()
    #kill serv
    cmd="sudo killall servod"
    os.system(cmd)

    print('exit')
    sys.exit(0)

#サーボの初期化処理
def init_serv() :
    #servの初期化処理
    """
    pathdir=os.path.dirname(os.path.abspath(__file__))
    path1="/PiBits/ServoBlaster/user/servod --p1pins=7 --pcm"
    pathsudo="sudo "
    pathkill="sudo killall servod"
    path=pathsudo+pathdir+path1
    print(path)
    """

    cmd = "sudo "+SERVD_PATH+" --p1pins=7 --pcm"
    os.system(cmd)


#mainプログラム
if __name__== '__main__':
    #write json test
    
    """
    d={'PATTERN':1, 'CNTRL':'1', 'TIME':20}
    print(d)
    with open('../dat/serv_req.json', 'w') as f:
        json.dump(d, f, indent=4)
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
            #os.remove(SERV_REQ)
            update_serv_cntrl(d)
        
        sleep(SAMPLING_TIME)