from . import views
from django.urls import path

urlpatterns = [
    path('recommend_crop/',views.crop_recommend,name='recommend'), 
]