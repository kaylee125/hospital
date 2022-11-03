from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def symptom_input(request):
    return HttpResponse('증상입력')

def symptom_choice(request):
    return HttpResponse('증상선택')

def check_dpt(request):
    return  HttpResponse('진료과목 확인')

def addr_input(request):
    return HttpResponse('주소입력')

def recommend_hos(request):
    return HttpResponse('추천병원')

def hos_info(request):
    return HttpResponse('병원별 정보제공')

def get_hos_map(request):
    return HttpResponse('주변 병원 지도 표현')

def save_hos_info(request):
    return HttpResponse('병원 기록별 저장')

