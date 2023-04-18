from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

app_name='accounts'

urlpatterns = [
    path('signup/', views.signup,name='signup'),
    # path('login/', views.signin ,name='login'),
    # path('logout/', views.logout,name='logout'),
    path('login/',  auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile,name='profile'),
    path('my_record/', views.my_record,name='my_record')


]
  