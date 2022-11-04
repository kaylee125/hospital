from django.contrib import admin
from django.urls import path,include
from . import views

app_name='accounts'

urlpatterns = [
    path('signup/', views.signup,name='signup'),
    path('login/', views.signin ,name='login'),
    path('logout/', views.logout,name='logout'),
    path('profile/', views.profile,name='profile'),


]
