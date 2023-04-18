from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#UserForm: django.contrib.auth.forms 모듈의 UserCreationForm 클래스를 상속하여 만든 클래스
#UserCreationForm의 속성: username,password1,password2 
class UserForm(UserCreationForm):
    email = forms.EmailField(label='email')

    class Meta:
        model = User
        fields = ("username", "password1", "password2","email")