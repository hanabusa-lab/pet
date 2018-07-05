from django.db import models

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
    pet = models.ForeignKey(PetInfo, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='images/', default='images/blank.png')
    date = models.DateTimeField(auto_now=False)
    tag_id = models.IntegerField(default=0)
    unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE)
    comment = models.CharField(max_length=256)
    def __str__(self):
        return self.pet.name+" "+self.date.strftime('%Y-%m-%d %H:%M')
    