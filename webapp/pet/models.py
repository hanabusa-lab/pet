from django.db import models
import os
import shutil
# Create your models here.

class PetInfo(models.Model):
    pet_id = models.IntegerField(default=0)
    tag_id = models.IntegerField(default=0)
    name = models.CharField(max_length=64)
    owner = models.CharField(max_length=64)
    address = models.CharField(max_length=128)
    birth_day = models.DateField(auto_now=False)
    favorite = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class PetFriend(models.Model):
    pet = models.ForeignKey(PetInfo, on_delete=models.CASCADE,related_name='pet')
    friend_pet = models.ForeignKey(PetInfo, on_delete=models.CASCADE,related_name='friend')
    def __str__(self):
        return self.pet.name+" "+self.friend_pet.name

class UnitInfo(models.Model):
    unit_id = models.IntegerField(default=0)
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=128)
    def __str__(self):
        return self.name

class PetImage(models.Model):
    CHECK_STATUS_NOCHECK = 0
    CHECK_STATUS_OK= 1
    CHECK_STATUS_NG = 2
    
    pet = models.ForeignKey(PetInfo, on_delete=models.CASCADE, null=True)
    img = models.ImageField(upload_to='pet/img', default='pet/img')
    date = models.DateTimeField(auto_now=True, null=True)
    tag_id = models.IntegerField(default=0, null=True)
    unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, null=True)
    comment = models.CharField(max_length=256, null=True)
    check_status = models.IntegerField(default=0, null=True)
    eval_result = models.CharField(max_length=256, null=True)

    #def __str__(self):
    #    return self.pet.name+" "+self.date.strftime('%Y-%m-%d %H:%M')

    def move2checked_dir(self) :
        filepath = str(self.img)
        print("org filename=", filepath)
        path = os.path.dirname(filepath)
        base =os.path.basename(filepath) 
        print(path, base)
        if os.path.exists("media/"+filepath) :
            print("file_exist","media/"+filepath)
            shutil.move("media/"+filepath, "media/pet/pet_img/"+base)
            self.img = "pet/pet_img/"+base;
    
        else :
            print("file_not_exist","media/"+filepath)
        
        pass
         

