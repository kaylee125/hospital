from django.http import HttpResponse

def index(request):
    return HttpResponse('메인페이지')