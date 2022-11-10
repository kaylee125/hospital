import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from accounts.forms import UserForm
from django.contrib.auth import authenticate,login
from django.http import HttpResponse

#회원가입
def signup(request):

   
    if request.method == "GET":
        form = UserForm()
        return render(request, 'accounts/signup.html', {'form': form})

    form = UserForm(request.POST)

     #POST로 받았는데 유효성검사 결과 false인 경우 
    if not form.is_valid():
        return render(request, 'accounts/signup.html', {'form': form})

    #POST로 정상적으로 데이터 받은 경우 db에 user정보 저장
    form.save()
    username = form.cleaned_data.get('username')
    raw_password = form.cleaned_data.get('password1')
    #신규사용자인증 및 자동로그인 기능
    user = authenticate(username=username, password=raw_password)  # 사용자 인증
    login(request, user)  # 로그인
    return redirect('/')
            
#로그인
 #post방식으로 받으면  계정정보가 있는지 확인해주고 정보가 있다면 로그인,
 # 그렇지 않다면 login창으로 돌아가 에러메세지 출력을 위한 메세지 보내기
# def signin(request):

#     #입력한 username, password 에 해당되는계정정보를 있는지 확인
#     if request.method=="POST":
        
#         username=request.POST['username']
#         password=request.POST['password']
#         print(password)
#         user = authenticate(username=username, password=password)
#         if user is not None: #유저가 db에 있는 경우 로그인 시켜줌
#             login(request,user)
#             return redirect('/')
#         else:
#             # 계정정보 없는 경우 login으로 돌아가 에러 메세지를 출력해주기 위해 메세지를 보냄
#             return render(request,'accounts/login.html',{'error':'username or password is incorrect'})
#     else:
#         return render(request,'accounts/login.html')

    
# def logout(request):
#     if request.user.is_authenticated:
#         print(request.user.is_authenticated)
#         logout(request)
#         return redirect('/')
    # if request.session['user']:
    #     del(request.session['user'])
    # return redirect('/')
    # if request.method=="POST":

    # return render(request,'accounts/login.html')


def profile(request):
    return render(request,'accounts/profile.html')
