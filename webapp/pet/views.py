from django.shortcuts import render
import django_filters
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
import sys,os
import json
sys.path.append("imgEvaluator")
from imgprocessor import ImgProcessor

# Create your views here.
from django.http import HttpResponse
from .models import *
from .serializer import *

def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    return render(request, "index.html")

class PetImageViewSet(viewsets.ModelViewSet):
    queryset = PetImage.objects.all()
    serializer_class = PetImageSerializer

    @action(methods=['post'], detail=False)
    def post_img(self, request, pk=None):
        serializer = PetImageSerializer(data=request.data)
        
        if  serializer.is_valid():
            new_serializer=serializer.create(serializer.validated_data)
            return Response(new_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'succeeded': True})
  
    #画像評価のチェックの実行
    @action(methods=['post'], detail=False)
    def check_img(self, request, pk=None):
        max_cnt = 100
        print(request.data)
        if "num" in request.data :
            max_cnt = int(request.data['num'])
            print("max_cnt", max_cnt)

        #PetImageで未チェックのものを取得する。
        nocheck_list  = PetImage.objects.all().filter(check_status=0)
        #nocheck_list = PetImage.objects.all()
        #チェックの実施
        imgProcessor = ImgProcessor()

        print("no check len=", len(nocheck_list))
        
        cnt = 0;
        for img in nocheck_list:
            print(str(img.img))
            jfile = "tmp_img_result.json"
            if os.path.exists("media/"+str(img.img)) :
                print("exec imgProcess")
                imgProcessor.proc("media/"+str(img.img), jfile)
                #imgProcessor.proc('2.jpg', "tmp_img_result.json")
            else :
                print("file not exist.", "media/"+str(img.img))
        
            df = ""
            #jsonの結果を確認
            with open(jfile) as f:
            #with open("tmp_img_result1.json") as f:
                jd = json.load(f)
                f.close
            
            x = int(jd['picture info']['x'])
            #犬と認識されない場合
            if x ==  -1 :
                print("x=-1", "no dog")
                img.delete()
                os.remove("media/"+str(img.img))
                #delete db and image            
                
                   #jd = json.loads("tmp_img_result1.json")
                #print(jd['x'])
            
            #犬と認識された場合
            if x!= -1 :
                print("score=",jd['picture info']['score'], " find dog")
                print("date=", img.date)
                img.check_status = 1
                js = json.dumps(jd)
                img.eval_result = js
                img.move2checked_dir()
                img.save()
        
            cnt+=1
           # img.check_status = 1
            if cnt >= max_cnt :
                print("achieve max cnt=", cnt, " max=", max_cnt)
                break   
            #チェックがOKだったものの属性を変える
            #img.move2checked_dir()
            #img.save()
    
        return Response({'succeeded': True})
    
    #チェック済画像リストの取得    
    @action(methods=['get'], detail=False)
    def get_checked_imglist(self, request):
        #要求の候補。数、Pet対象、お友達と一緒、取得時期
        list_num = 10
        img_list = PetImage.objects.all().filter(check_status=PetImage.CHECK_STATUS_OK).order_by('-date')
        
        json_img_list = {}
        for i in range(len(img_list)):
            #json_img_list[i] = str(img_list[i].img)
            jd = json.loads(img_list[i].eval_result)
            print(jd['picture info']['x'])
            #json_img_list[i] = '{"file":"'+ str(img_list[i].img)+'\", "x":"+str(jd['picture info']['x'])+",'y':"+str(jd['picture info']['y'])+ ",'width':"+str(jd['picture info']['width'])+",'height':"+str(jd['picture info']['height'])+ "}"
            json_img_list[i] = '{"file":"'+ str(img_list[i].img)+'\", "x":'+str(jd['picture info']['x'])+',"y":'+str(jd['picture info']['y'])+ ',"width":'+str(jd['picture info']['width'])+',"height":'+str(jd['picture info']['height'])+ '}'
            #json_img_list[i] = '{"file":"a"}' 
            #json_img_list[i] = str(img_list[i].img)

        '''
        if  serializer.is_valid():
            new_serializer=serializer.create(serializer.validated_data, true)
            return Response(new_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        '''
        return Response(json_img_list, status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def fullnames(self, request):
        return Response([
            '{petimg.comment}'.format(petimg=petimg)
            for petimg in self.get_queryset()
        ])