#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import mercury
import os
import sys
from datetime import datetime
import RPi.GPIO as GPIO
import picamera

#定義関連
SWITCH_IO = 17  #スイッチのGPIOピン
SERV_IP = "172.20.10.6:8080" #サーバのIPアドレス
SERV_FG = False #サーバの有効化フラグ
TAG_FG = True   #タグの有効化フラグ

#グローバル変数
gcamera = ""
greader = ""

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
    global gcamera

    #ファイル名称の作成
    now= datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = '/pet/dat/'+now+'_'+str(tagid)+".jpg"
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

        #"http://localhost:8080/pet/api/check_img/" -d "num=2"


if __name__== '__main__':
    #パラメータの初期化
    swchfg = ""

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
            print("tagid=",tagid)
            capture_send_img(tagid)
        
    
        time.sleep(0.5)        
    '''
    #tag readerの初期化
    #init_tag_reader()

    #Cameraの初期化

    #実行ループの開始
    while 1 :
        
        #tag readerの読み込みチェック
        #print(reader.read(100))
        
        #tag readerの反応があった場合
        if tagreadFg == True  :
            capture_send_img()

        time.sleep(0.5)
        sys.exit()
    '''