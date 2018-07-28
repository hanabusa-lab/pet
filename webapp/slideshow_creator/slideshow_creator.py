# -*- coding: utf-8 -*-
from time import sleep
import os
import datetime
import subprocess
import pandas as pd
import requests
import pprint

#image listの取得
def get_image_list() :
    response = requests.get('http://localhost:8080/pet/api/get_checked_imglist/',params={'num': '4'})
    res = response.json()
    print(len(response.json()))
    pprint.pprint(response.json()) 
    return response.json()
    
#指定イメージを用いた動画作成
def convert2slide(file):
    '''
    cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i ../media/pet/pet_img/2.jpg -filter_complex \"zoompan=  x='iw-iw/zoom':  y='ih-ih/zoom':  z='if(eq(on,1),1.2,zoom-0.002)':  d=25*4:s=1280x800\" -pix_fmt yuv420p -c:v libx264   -vcodec libx264   -movflags faststart   -vprofile baseline -level 3.0   -g 150   -b:v 519k   -s 768x432   -acodec aac   -b:a 63.4k   -ar 44100   -flags +loop-global_header  -hls_time 5 -hls_list_size 5 -hls_flags append_list+omit_endlist+delete_segments   ../media/stream/playlist.m3u8"
    '''

    cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i "+file+" -filter_complex \"zoompan=  x='iw-iw/zoom':  y='ih-ih/zoom':  z='if(eq(on,1),1.2,zoom-0.002)':  d=25*4:s=1280x800\" -pix_fmt yuv420p -c:v libx264   -vcodec libx264   -movflags faststart   -vprofile baseline -level 3.0   -g 150   -b:v 519k   -s 768x432   -acodec aac   -b:a 63.4k   -ar 44100   -flags +loop-global_header  -hls_time 5 -hls_list_size 5 -hls_flags append_list+omit_endlist+delete_segments   ../media/stream/playlist.m3u8"

    #print(cmd)
    proc = subprocess.call( cmd , shell=True)
    #subprocess.call(["/usr/local/opt/ffmpeg/bin/ffmpeg", option])
    

if __name__== '__main__':
    imglist = get_image_list()
    
    for id in imglist :
        file = "../media/"+imglist[id]
        convert2slide(file)
        print(file) 
    
    
    #while 1 :
        #init param

        #print("auau")
        #if trick_kind change, reload sound
        #if pre_trick_kind != trick_kind :
        #   strick.set_sound(trick_kind) 
        
        #update save bin img txt
       # sleep(1)
