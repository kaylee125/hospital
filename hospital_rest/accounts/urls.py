from django.contrib import admin
from django.urls import path,include
from . import views

appname='accounts'

urlpatterns = [
    path('signup/', views.signup),
    path('login/', views.signin),
    path('logout/', views.logout),
    path('profile/', views.profile),


]
