from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserForm(UserCreationForm):
    id=forms.CharField(label='아이디'),
    password=forms.CharField(label='비밀번호'),
    email = forms.EmailField(label='이메일'),
    gender=forms.CharField(label='성별'),
    age=forms.CharField(label='나이대'),
    addr_sigungu=forms.CharField(label='시군구주소')

    class Meta:
        model = User
        fields = ['username', 'email']
        #id, password, email,gender,age,addr_sigungu