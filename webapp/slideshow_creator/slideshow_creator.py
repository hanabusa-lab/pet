# -*- coding: utf-8 -*-
from time import sleep
import time
import os, sys
import datetime
import subprocess
import pandas as pd
import requests
import pprint
import json
from PIL import Image
from datetime import datetime
import glob
from operator import itemgetter

#定数
GET_IMG_NUM = 30 #IMAGEの取得数
EXEC_TIME =  1000 #実行時間(秒)
ONE_SLIDE_TIME = 2 #一つのスライドの時間。動画作成に用いる。
SLIDE_DELAY_TIME = 1 #次のスライドを作成する際の時間間隔

STREAM_DIR = "../media/stream/"

#新しい画像のリスト
NEW_LIST = []
NEW_LIST_NUM=5
NEW_LIST_INDX=0
TMP_INDX=0

#image listの取得
def get_image_list(num) :
    response = requests.get('http://localhost:8080/pet/api/get_checked_imglist/',params={'num': str(num)})
    res = response.json()
    #print("list le =", len(response.json()))
    #pprint.pprint(response.json()) 
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
            
    #一回、動画を作って、からtsファイルに追加した方が良さそう
    #動画作成
    """
    cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -y -i "+file+" -filter_complex \"zoompan="+opx+":"+opy+":  z='zoom+0.002':  d=25*"+str(ONE_SLIDE_TIME)+":s=800x600\"  out.mp4"
    """

    cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -y -i "+file+" -filter_complex \"[0:v]scale=8000x6000,zoompan="+opx+":"+opy+":  z='zoom+0.002':  d=25*"+str(ONE_SLIDE_TIME)+":s=800x600\"  out.mp4"

    print(cmd)
    proc = subprocess.call( cmd , shell=True)
    #subprocess.call(["/usr/local/opt/ffmpeg/bin/ffmpeg", option])

    #動画にロゴを入れる
    cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg  -y -i  out.mp4 -i logo_small.png -filter_complex [1:v]lut=a='val*0.8',[0:v]overlay=W-w-20:H-h-20 out2.mp4"
    #cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg  -y -i  out.mp4 -i logo_small.png  overlay=W-w-20:H-h-20 out2.mp4"
   
    print(cmd)
    proc = subprocess.call( cmd , shell=True)

    #m3u8ファイルへの追加
    cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i  out2.mp4 -pix_fmt yuv420p -c:v libx264   -vcodec libx264   -movflags faststart   -vprofile baseline -level 3.0   -g 150   -b:v 519k   -s 768x432   -acodec aac   -b:a 63.4k   -ar 44100   -flags +loop-global_header  -hls_time 1.8 -hls_list_size 2 -hls_flags append_list+omit_endlist+delete_segments   ../media/stream/playlist.m3u8"
    print(cmd)
    proc = subprocess.call( cmd , shell=True)

    #tsファイルに対して、ロゴを追加する。→これだと、ロゴが反映されなかった。
    """
    latest_file = get_latest_ts()
    cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg  -y -i "+latest_file+" -i logo_small.png -filter_complex [1:v]lut=a='val*0.7',[0:v]overlay=W-w-20:H-h-20 out.ts"
    print(cmd)
    proc = subprocess.call( cmd , shell=True)
    #ファイルをリネーム
    os.rename("out.ts", latest_file)
    """

#最新のtsファイルを取得する
def get_latest_ts() : 
    filenames = glob.glob(os.path.join(STREAM_DIR,'*.ts'))

    file_list = []
    for file in filenames:
        #file = os.path.join(STREAM_DIR,file)
        #print("file=",file)
        dt = datetime.fromtimestamp(os.stat(file).st_mtime)
        file_list.append([file,str(dt)])

    lst = sorted(file_list,key=itemgetter(1), reverse = True)
    """
    for file in lst:
        print(file)
   """
    #print(lst[0][0])
    return lst[0][0]

#定義ファイル指定のファイルリストを生成する
def create_spec_slide_list():
    #表示リストの読み込み
    with open('slide_list.json') as f:
        speclist = json.load(f)
    pprint.pprint(speclist, width=40)
    for id in speclist :
        #print(id)
        jd = speclist[id]
        print(jd['file'], jd['x'], jd['y'], jd['width'], jd['height'])
    return speclist

#サーバから新しい画像を取得する
def get_newitem() :
    global NEW_LIST_INDX, NEW_LIST, TMP_INDX
    #新しいのがあったら、新しいのを返して、新しいのがなかったら、リストのものを順番に返す。

    imglist = get_image_list(1)
    jd = json.loads(imglist['0'])
    findfg = False
    #print("imglist=",type(imglist),imglist)
    
    """
    jd = json.loads(imglist[str(TMP_INDX)])
    TMP_INDX+=1
    if TMP_INDX>9:
        TMP_INDX=0
    """

    #print("jd=",jd)
    
    for dat in NEW_LIST :
         if dat['file'] == jd['file'] :
            findfg = True
            print("find item", jd['file'])
            break

    #項目がすでにある場合には、現在のインデックスで対象を取得する
    if findfg == True :
        print("exising INDEX=",NEW_LIST_INDX, "NEW_LIST=",NEW_LIST)
        jd = NEW_LIST[NEW_LIST_INDX]
        NEW_LIST_INDX+=1
        if NEW_LIST_INDX > len(NEW_LIST)-1    :
            NEW_LIST_INDX = 0
        print("jd=",jd)
        return jd 
    
    if findfg == False:
        NEW_LIST.insert(0, jd)
        if len(NEW_LIST) > NEW_LIST_NUM :
            NEW_LIST.pop(-1)
        print("added new_list num=",len(NEW_LIST), NEW_LIST)
        return jd
    
#slide showのメインプログラム
if __name__== '__main__':
    #get_latest_ts()
    #sys.exit()

    #imglist = get_image_list(200)
    #sys.exit()
    #GUGEN
    #定義ファイルのリストを取得する
    speclist = create_spec_slide_list()
    #print("speclist=",type(speclist),speclist)
    #speclist = json.load(speclist)
    #開始時間の取得
    starttime = datetime.now()

    #実行ループ
    newitemcnt = 0
    newimgtiming = 3
   
    cnt=0
    while True:
        #定義ファイルリストの分だけ実行する
        #最新のリストを入れ込むタイミングを指定する。
        prelastimg=""
        for spec in speclist :
            #最新の画像があったら、まずは、それを表示する
            imglist=get_image_list(1)
            jd =json.loads(imglist['0'])
            #print("last img=", jd['file'])
            if jd['file'] != prelastimg :
                convert2slide("../media/"+jd['file'], jd['x'], jd['y'], jd['width'], jd['height'])
                prelastimg = jd['file']

            #最新のリストのチェック 
            #print("=convimg old= newitemcnt =",newitemcnt, newimgtiming)
            if newitemcnt >= newimgtiming  :
                newitemcnt = 0
                #最新のリストを取得する
                jd = get_newitem()
                #sys.exit()
                print('=convimg new= create new img from!! get_newitem=',jd['file'])
                convert2slide("../media/"+jd['file'], jd['x'], jd['y'], jd['width'], jd['height'])
            
            #print("spec=",spec,speclist[spec]['file'])
            jd = speclist[spec]
            convert2slide("../media/"+jd['file'], jd['x'], jd['y'], jd['width'], jd['height'])
            newitemcnt+=1
        """
        cnt+=1
        if  cnt>1:
            sys.exit()
        """

    """
    #ORIGINAL
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
        
        #終了時間の確認
        now = datetime.now()
        diftime = now - starttime
        if diftime.total_seconds()  > EXEC_TIME :
            print("exec time.")
            sys.exit()

        #次回の処理とのディレイ
        sleep(GET_IMG_NUM*ONE_SLIDE_TIME)
        """
           
