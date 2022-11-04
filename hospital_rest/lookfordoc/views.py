from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    # return HttpResponse('메인페이지')
    return render(request,'index.html')

