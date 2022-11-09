from django.contrib import admin
from django.urls import path,include
from . import views

app_name='recommend'

urlpatterns = [
    path('symptominput/', views.symptom_input ,name='symptominput'),
    path('symptomchoice/', views.symptom_choice,name='symptom_choice'),
    path('check/', views.check_dpt,name='check_dpt'),
    path('addrinput/', views.addr_input,name='addr_input'),
    path('hoslist/', views.recommend_hos,name='recommend_hos'),
    path('hosinfo/<str:get_param>/<str:param>', views.hos_info,name='hos_info'),
    # path('map/', views.get_hos_map,name='get_hos_map'),
    path('recode/', views.save_hos_info,name='save_hos_info'),

]


