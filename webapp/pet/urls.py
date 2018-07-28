from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers

from . import views
from .views import *

app_name='pet'

router = routers.DefaultRouter()
#router.register(r'petimage', PetImageViewSet)
router.register(r'api', PetImageViewSet)


urlpatterns = [
    path('', views.index, name='index'),
    url(r'^', include(router.urls)),
    #url(r'^api/$', views.PetImageViewSet),
]

