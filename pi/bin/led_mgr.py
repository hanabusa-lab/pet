# -*- coding: utf-8 -*-
from time import sleep
import time
import os
import  json
import pprint
import threading
import signal
import sys
from neopixel import *
from pet_def import *
import datetime
import fasteners

#定数定義
SAMPLING_TIME=0.2           #サンプリングタイム
LED_REQ='../dat/led_req.json' #LEDリクエストファイル
# LED strip configuration:
#LED_COUNT      = 16      # Number of LED pixels.
LED_COUNT      = 2      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 25     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53



#グローバル変数
gthread_led = ""
gthread_enablefg = True #スレッドの有効フラグ
gled_cntrl = 0  #0:None, 1:START, 2:STOP
gled_pattern = 0
gled_time = 0
gled_color = (0,0,0)
gled_start_time = None
glock =""   #Lockファイル

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def colorBright(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for j in range(20):
        for i in range(strip.numPixels()):
            if (i+j)%2 == 0 :
                strip.setPixelColor(i, color)
            else :
                strip.setPixelColor(i, Color(0,0,0)) 
            strip.show()
        time.sleep(wait_ms/1000.0)

def colorBright2(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for j in range(5):
        for i in range(strip.numPixels()):
            if (i+j)%2 == 0 :
                strip.setPixelColor(i, color)
            else :
                strip.setPixelColor(i, Color(0,0,0)) 
            strip.show()
        time.sleep(wait_ms/1000.0)


#jsonファイルのパース処理
def parse_req_file(filename) :
    with open(LED_REQ) as f:
        d = json.load(f)
    pprint.pprint(d, width=40)
    return d

#LEDスレッド
def exec_led_thread() :
    global gthread_enablefg, gled_cntrl, gled_pattern, gled_time, gled_color

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    #clear pre color
    colorWipe(strip, Color(0, 0, 0))

    while 1 :
        if gthread_enablefg == False :
            colorWipe(strip, Color(0, 0, 0))
            print("end exec_led_thread")
            return
         
        #停止処理の場合  
        if gled_cntrl ==  LEDCntrl.STOP:
            print("thred gled_stop")
            colorWipe(strip, Color(0, 0, 0))
            sleep(SAMPLING_TIME)
            continue
 
        #経過時間のチェック
        if gled_start_time != None and gled_time > 0:
            now = datetime.datetime.now()  
            diftime = now - gled_start_time  
            if diftime.total_seconds() > gled_time :
                colorWipe(strip, Color(0, 0, 0))
                sleep(SAMPLING_TIME)
                print("thred time passed")
                continue
 
        #モードごとの実行
        if gled_pattern == LEDPattern.WIPE : 
            print("thread exec color Wipe ", gled_color)
            colorWipe(strip, Color(gled_color[1], gled_color[0], gled_color[2])) 
            sleep(SAMPLING_TIME)
            continue
        
        if gled_pattern == LEDPattern.BRIGHT :
            print("thread exec color Bright ", gled_color)    
            colorBright(strip, Color(gled_color[1], gled_color[0], gled_color[2])) 
 
        if gled_pattern == LEDPattern.BRIGHT2:
            print("thread exec color Bright2 ", gled_color)    
            colorBright2(strip, Color(gled_color[1], gled_color[0], gled_color[2]), 500) 


        
#LEDコントロール情報の更新
def update_led_cntrl(d): 
    global gled_cntrl, gled_pattern, gled_time, gled_color, gled_start_time

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

    #時間の確認
    if d.get('TIME') != None :
        gled_time = float(d.get('TIME'))
        #Timeが指定されている場合には時間を更新する。
        gled_start_time =  datetime.datetime.now()    
    else :
        #Timeが設定されていない場合には、開始時間をNoneに設定する。
        gled_start_time = None
    
    print("update_led_cntrl. cntrl",gled_cntrl, "pattern", gled_pattern, "time", gled_time, "color", gled_color)
        
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
    
    #ロックファイルの作成
    glock = fasteners.InterProcessLock('/tmp/lockfile')
    """
    d={'PATTERN':1, 'COLOR':(1,2,3), 'CNTRL':'1', 'TIME':20}
    print(d)
    with open('../dat/led_req.json', 'w') as f:
        json.dump(d, f, indent=4)
    """
    """    
    print("enum test", LEDCntrl.NONE)
    if LEDCntrl.NONE == 0 :
        print("enum test ok", LEDCntrl.NONE)
    """
    
    #シグナルハンドラの登録(Cntrl+Cを受け取った際の終了処理)
    signal.signal(signal.SIGINT, handler)

  
    #LEDスレッドの作成と実行
    gthread_led = threading.Thread(target=exec_led_thread)
    gthread_led.start()
    
    #実行ループ(ファイルチェック)
    while 1 :
        print("file check")
        #check conf file
        if os.path.exists(LED_REQ) == True :
            print("file exist") 
            glock.acquire()
            d=parse_req_file(LED_REQ)
            os.remove(LED_REQ)
            glock.release()

            update_led_cntrl(d)
        
        sleep(SAMPLING_TIME)
