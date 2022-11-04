from django.contrib import admin
from django.urls import path,include
from . import views

app_name='recommend'

urlpatterns = [
    path('symptominput/', views.symptom_input),
    path('symptomchoice/', views.symptom_choice),
    path('check/', views.check_dpt),
    path('addrinput/', views.addr_input),
    path('hoslist/', views.recommend_hos),
    path('hosinfo/', views.hos_info),
    path('map/', views.get_hos_map),
    path('recode/', views.save_hos_info),

]


