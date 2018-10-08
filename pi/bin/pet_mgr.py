#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import mercury
import os
import sys
#from datetime import datetime
import datetime
import RPi.GPIO as GPIO
import picamera
import  json
import pprint
from pet_def import *

#定義関連
TAG_COLOR_CONF = "../dat/tag_color.json"
LED_REQ_FILE = "../dat/led_req.json"
SWITCH_IO = 17  #スイッチのGPIOピン
#SERV_IP = "172.20.10.6:8080" #サーバのIPアドレス
SERV_IP = "192.168.3.9:8080" #サーバのIPアドレス
SERV_FG = True #サーバの有効化フラグ
TAG_FG = True   #タグの有効化フラグ
SHUTDOWN_TIME = 6

#グローバル変数
gcamera = ""
greader = ""
gtag_color = ""

#Tagの初期化
def init_tag_reader() :
    global greader
    #greader = mercury.Reader("tmr:///dev/ttyUSB0", baudrate=115200)
    greader = mercury.Reader("tmr:///dev/ttyUSB0", baudrate=19200)

    print(greader.get_model())
    print(greader.get_supported_regions())
    greader.set_region("JP")
    greader.set_read_plan([1], "GEN2", read_power=2000)

#reader.start_reading(lambda tag: print(tag.epc, tag.antenna, tag.read_count, tag.rssi))
#time.sleep(1)
#reader.stop_reading()

#カメラの初期化
def init_camera() :
    global gcamera
    gcamera = picamera.PiCamera()
    gcamera.resolution = (1024, 768)
    gcamera.rotation=90
    #camera.hflip=True
    
    
#画像の取得とサーバへの送信
def capture_send_img(tagid):
    global gcamera, gtag_color
    print("gtag_color",gtag_color, "tagid",tagid)

    color = (255,255,255)
    #LEDリクエスト
    if gtag_color.get(tagid) != None :
        color = gtag_color.get(tagid)
        print("color", color )         
    
    #LEDリクエストファイルの作成
    d={'PATTERN':int(LEDPattern.BRIGHT), 'COLOR':(color[0], color[1],color[2]), 'CNTRL':int(LEDCntrl.START), 'TIME':30}
    print(d)
    with open(LED_REQ_FILE, 'w') as f:
        json.dump(d, f, indent=4)

    #ファイル名称の作成
    now= datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = '/pet/img/'+now+'_'+tagid+".jpg"
    print("filename=", filename)
    #cmd = 'raspistill -w 1200 -h 900 -n -t 10 -q 100 -e jpg -o '+filename
    #os.system(cmd)
    
    #画像の取得
    gcamera.capture(filename)

    if SERV_FG == True :
        #サーバーへの画像の送信
        #cmd = curl -X POST -S   -H 'Accept: application/json'   -F "comment=test3"   -F "img=@/#pet/dat/out.png;type=image/png"   "http://172.20.10.6:8080/pet/api/post_img/"

        cmd = "curl -X POST -S   -H 'Accept: application/json'   -F 'comment=test3'   -F 'img=@"+filename+";type=image/jpg\' 'http://"+SERV_IP+"/pet/api/post_img/'"
        print(cmd)
        os.system(cmd)

        #サーバーに対して画像チェック依頼
        cmd = "curl -X POST -S 'http://"+SERV_IP+"/pet/api/check_img/' -d 'num=2'"
        print(cmd)
        os.system(cmd)

    #LEDリクエストのOFF
    print("off request")
    d={'CNTRL':int(LEDCntrl.STOP)}
    print(d)
    with open(LED_REQ_FILE, 'w') as f:
        json.dump(d, f, indent=4)

        #"http://localhost:8080/pet/api/check_img/" -d "num=2"

if __name__== '__main__':
    #global gtag_color
    #パラメータの初期化
    swchfg = ""
    preswchfg = ""
    swchpushtime =  datetime.datetime.now()

    #タグと色の対応づけ情報の取得
    with open(TAG_COLOR_CONF) as f:
        gtag_color = json.load(f)
        pprint.pprint(gtag_color, width=40)

    if gtag_color.get("E20040057305011623802048") != None :
        color = gtag_color.get("E20040057305011623802048")
        print("color", color )         

    
    #sys.exit()

    #gpioの初期化
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SWITCH_IO, GPIO.IN)
   
    #カメラの初期化
    init_camera()

    #Tagの初期化
    if TAG_FG == True:
        init_tag_reader() 
       
    #gcamera.capture('my_picture.jpg')

    while True:
        #変数の初期化
        taglist = ""
        tagid = ""

        #switchのチェック
        swchfg = GPIO.input(SWITCH_IO)
        print("io val=", swchfg)

        #Tagのチェック
        if TAG_FG == True:
            taglist =greader.read(100)
        
        #TAGの取得
        for tag in taglist :
            print(tag.epc, tag.antenna, tag.read_count, tag.rssi)
       
         #複数のワンちゃんがいたら、最初のワンちゃんを撮影する 
        if len(taglist) > 0 :
            tagid = taglist[0].epc
            print("tagid=",tagid, "strtagid", str(tagid), "strtagid2", str(tagid)[2:26])
            capture_send_img(str(tagid)[2:26])
        
        #Switchが押されていたら撮影を行う。
        if swchfg != preswchfg and  swchfg == 1:
            print("switch on. exec capture")
            capture_send_img("MANUAL")

        #swchが押された時点の状態を記録する。
        if swchfg != preswchfg :
            if swchfg == 1:
                swchpushtime =  datetime.datetime.now()
                #print("update swhchpushtime on =", swchpushtime)
            if swchfg == 0:
                swhchpushtime = ""
                #print("update swhchpushtime off=", swhchpushtime)
          
        #swchが押され続けていた時間が一定時間以上経過したらシャットダウン
        if swchfg == 1 and swchpushtime != "" :
            now = datetime.datetime.now()
            diftime = now - swchpushtime
            
            print(type(diftime), diftime, "dif time = ", diftime.total_seconds())
            if diftime.total_seconds() > SHUTDOWN_TIME :
                cmd = 'sudo shutdown -h now'
                print("exec shutdown", cmd)
                os.system(cmd)
            
        time.sleep(0.5)
        preswchfg = swchfg

        #sys.exit()