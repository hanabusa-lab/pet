# -*- coding: utf-8 -*-
from time import sleep
import os, sys
import datetime
import subprocess
import pandas as pd
import requests
import pprint
import json
from PIL import Image
from datetime import datetime

#定数
GET_IMG_NUM = 2 #IMAGEの取得数
EXEC_TIME =  60 #実行時間(秒)
ONE_SLIDE_TIME = 8 #一つのスライドの時間　この時間と枚数からplaylist.m3u8の更新間隔を決める。

#image listの取得
def get_image_list() :
    #response = requests.get('http://localhost:8080/pet/api/get_checked_imglist/',params={'num': '3'})  
    response = requests.get('http://localhost:8080/pet/api/get_checked_imglist/',params={'num': str(GET_IMG_NUM)})
    res = response.json()
    print("list le =", len(response.json()))
    pprint.pprint(response.json()) 
    return response.json()
    
#指定イメージを用いた動画作成
def convert2slide(file, roix, roiy, roiw, roih):
    #画像サイズの取得
    im = Image.open(file)
    print(im.size)
    
    '''
    cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i ../media/pet/pet_img/2.jpg -filter_complex \"zoompan=  x='iw-iw/zoom':  y='ih-ih/zoom':  z='if(eq(on,1),1.2,zoom-0.002)':  d=25*4:s=1280x800\" -pix_fmt yuv420p -c:v libx264   -vcodec libx264   -movflags faststart   -vprofile baseline -level 3.0   -g 150   -b:v 519k   -s 768x432   -acodec aac   -b:a 63.4k   -ar 44100   -flags +loop-global_header  -hls_time 5 -hls_list_size 5 -hls_flags append_list+omit_endlist+delete_segments   ../media/stream/playlist.m3u8"
    '''
    """
    cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i "+file+" -filter_complex \"zoompan=  x='iw-iw/zoom':  y='ih-ih/zoom':  z='if(eq(on,1),1.2,zoom-0.002)':  d=25*4:s=1280x800\" -pix_fmt yuv420p -c:v libx264   -vcodec libx264   -movflags faststart   -vprofile baseline -level 3.0   -g 150   -b:v 519k   -s 768x432   -acodec aac   -b:a 63.4k   -ar 44100   -flags +loop-global_header  -hls_time 5 -hls_list_size 5 -hls_flags append_list+omit_endlist+delete_segments   ../media/stream/playlist.m3u8"
    """
    
    #ROIからズーム位置を設定する
    cx = int(roix+roiw/2)
    cy = int(roiy+roih/2)
    opx = ""
    opy = ""
    print("cx=",cx," cy=",cy, " imx=", im.size[0], " imy=", im.size[1])
    if cx >= im.size[0]/2 :
        opx ="x=\'"+str(cx)+"+("+str(cx)+"/zoom)\'"
    else :
        opx ="x=\'"+str(cx)+"-("+str(cx)+"/zoom)\'"
    print(opx)
    
    if cy >= im.size[1]/2 :
        opy ="y=\'"+str(cy)+"+("+str(cy)+"/zoom)\'"
    else :
        opy ="y=\'"+str(cy)+"-("+str(cy)+"/zoom)\'"
            

    cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i "+file+" -filter_complex \"zoompan="+opx+":"+opy+":  z='zoom+0.002':  d=25*"+str(ONE_SLIDE_TIME)+":s=800x600\" -pix_fmt yuv420p -c:v libx264   -vcodec libx264   -movflags faststart   -vprofile baseline -level 3.0   -g 150   -b:v 519k   -s 768x432   -acodec aac   -b:a 63.4k   -ar 44100   -flags +loop-global_header  -hls_time 5 -hls_list_size 5 -hls_flags append_list+omit_endlist+delete_segments   ../media/stream/playlist.m3u8"
    
    print(cmd)
    proc = subprocess.call( cmd , shell=True)
    #subprocess.call(["/usr/local/opt/ffmpeg/bin/ffmpeg", option])
    
#slide showのメインプログラム
if __name__== '__main__':

    #開始時間の取得
    starttime = datetime.now()

    #実行ループ
    while True:
        #リストの取得
        imglist = get_image_list()
       
        cnt = 0
        for id in imglist :
            #file = "../media/"+imglist[id]['file']
            print(imglist[id])
            jd = json.loads(imglist[id])
            print(jd['file'], jd['x'], jd['y'], jd['width'], jd['height'])
            #print(jd['file']) 
            convert2slide("../media/"+jd['file'], jd['x'], jd['y'], jd['width'], jd['height'])
            #sys.exit()
            
            cnt+=1
            if cnt > 5 :
                break
        
        #終了時間の確認
        now = datetime.now()
        diftime = now - starttime
        if diftime.total_seconds()  > EXEC_TIME :
            print("exec time.")
            sys.exit()

        #次回の処理とのディレイ
        sleep(GET_IMG_NUM*ONE_SLIDE_TIME)
           
