import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from accounts.forms import UserForm
from django.contrib.auth import authenticate,login
from django.http import HttpResponse

def signup(request):
    if request.method=='POST':
        form=UserForm(request.POST)
        if form.is_valid():
    form.save()

            id = form.cleaned_data.get('id')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            addr_sigungu = form.cleaned_data.get('addr_sigungu')
            age = form.cleaned_data.get('age')
            user = authenticate(username=id, password=password)
            login(request, user)
    return redirect('/')
            
    return render(request, 'accounts/signup.html', {'form': form})

        

    
def signin(request):
    return render(request,'accounts/login.html')



def profile(request):
    return render(request,'accounts/profile.html')
