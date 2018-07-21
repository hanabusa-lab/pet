# coding: utf-8

from rest_framework import serializers

from .models import *


class PetImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetImage
        #fields = ('id', 'pet', 'img', 'comment')
        fields = ('id', 'img', 'comment')
        
    def create(self, validated_data):
        petImage = PetImage()
        petImage.comment=validated_data['comment']
        fname =  "media/pet/pet_precheck_img/"+str(validated_data['img'])
        petImage.img =  "pet/pet_precheck_img/"+str(validated_data['img'])
        
        with open(fname,'wb') as f:
            f.write(validated_data['img'].read())
            f.close()

        petImage.save()
        return PetImageSerializer(petImage)