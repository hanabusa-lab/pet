#!/usr/bin/env python3
from __future__ import print_function
import time
import mercury
import os
import sys
from datetime import datetime

SERV_IP = "172.20.10.6:8080"

#Tagの初期化
def init_tag_reader() :
    reader = mercury.Reader("tmr:///dev/ttyUSB0", baudrate=115200)
    print(reader.get_model())
    print(reader.get_supported_regions())
    reader.set_region("JP")
    reader.set_read_plan([1], "GEN2", read_power=2000)

#reader.start_reading(lambda tag: print(tag.epc, tag.antenna, tag.read_count, tag.rssi))
#time.sleep(1)
#reader.stop_reading()

#カメラの初期化
def init_camera() :
    pass

if __name__== '__main__':
    #tag readerの初期化
    #init_tag_reader()

    #読み取りループの開始
    while 1 :
        
        #tag readerの読み込みチェック
        #print(reader.read(100))
        
        #tag readerの反応があった場合

        #画像の取得
        now= datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = '/pet/dat/'+now+".jpg"
        print(filename)
        cmd = 'raspistill -w 1200 -h 900 -n -t 10 -q 100 -e jpg -o '+filename
        os.system(cmd)

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

        time.sleep(0.5)
        sys.exit()

        


    
