# -*- coding: utf-8 -*-
from time import sleep
import os
import  json
import pprint
import threading
import signal
import sys

#定数定義
SAMPLING_TIME=0.5           #サンプリングタイム
LED_REQ='../dat/led_req.json' #LEDリクエストファイル

#グローバル変数
gthread_led = ""
gthread_enablefg = True #スレッドの有効フラグ
gled_cntrl = 0  #0:None, 1:START, 2:STOP
gled_pattern = 0
gled_time = 0
gled_color = (0,0,0)

#jsonファイルのパース処理
def parse_req_file(filename) :
    with open(LED_REQ) as f:
        d = json.load(f)
    pprint.pprint(d, width=40)
    return d

#LEDコントロール情報の更新
def update_led_cntrl(d): 
    global gled_cntrl, gled_pattern, gled_time, gled_color

    print("exec_led_cnrl arg=",d)

    #コントロールモードの確認
    if d.get('CNTRL') != None :
         gled_cntrl = int(d.get('CNTRL'))

    #実行パターンの確認
    if d.get('PATTERN') != None :
         gled_pattern = int(d.get('PATTERN'))

    #色の確認
    if d.get('COLOR') != None :
         gled_color = (d.get('COLOR')[0], d.get('COLOR')[1], d.get('COLOR')[2])

    #色の確認
    if d.get('TIME') != None :
         gled_time = int(d.get('TIME'))
    
    print("cntrl",gled_cntrl, "pattern", gled_pattern, "time", gled_time, "color", gled_color)

#LEDスレッド
def exec_led_thread() :
    global gthread_enablefg, gled_cntrl, gled_pattern, gled_time, gled_color

    while 1 :
        if gthread_enablefg == False :
            print("end exec_led_thread")
            return

        print("LED")
        sleep(SAMPLING_TIME)
        
#終了処理
def handler(signal, frame):
    global gthread_led, gthread_enablefg
    gthread_enablefg = False
    gthread_led.join()
    print('exit')
    sys.exit(0)

#mainプログラム
if __name__== '__main__':
    #write json test
    
    """
    d={'PATTERN':1, 'COLOR':(1,2,3), 'CNTRL':'1', 'TIME':20}
    print(d)
    with open('../dat/led_req.json', 'w') as f:
        json.dump(d, f, indent=4)
    """

    #シグナルハンドラの登録(Cntrl+Cを受け取った際の終了処理)
    signal.signal(signal.SIGINT, handler)

    #LEDスレッドの作成と実行
    gthread_led = threading.Thread(target=exec_led_thread)
    gthread_led.start()
    
    #実行ループ(ファイルチェック)
    while 1 :
        #check conf file
        if os.path.exists(LED_REQ) == True :
            d=parse_req_file(LED_REQ)
            #os.remove(LED_REQ)
            update_led_cntrl(d)
        
        sleep(SAMPLING_TIME)