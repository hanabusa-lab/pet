from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(PetInfo)
admin.site.register(PetFriend)
admin.site.register(PetImage)
admin.site.register(UnitInfo)



