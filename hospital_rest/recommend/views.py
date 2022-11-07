from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from haversine import haversine
from recommend.models import HospitalInfo
from django.db.models import Q
import pandas as pd
import json

# Create your views here.


#증상입력: 텍스트로 입력 받고 모델결과 확인해서 결과가 잘 나오면 check_dpt로 render 안나오면 symptom_choice로 render
def symptom_input(request):
    #  인자로 받은 요청의 메소드가 POST라면 증상 입력값을 db에 저장 
    # if request.method =='POST':
    #     form = SymptomInputForm(request.POST)

    #             # 유효성 검사+모델 통과
    #     if form.is_valid():
    #         symptom = SymptomInputForm()
    #         symptom.symptominput = form.cleaned_data['symptominput']
    #         SymptomInputForm.save()
    #         return redirect('/')#이 부분 모델 결과에 따라 조건절로 redirect 다르게 설정하기

    # # GET이라면 입력값을 받을 수 있는 html을 가져다 줘야함
    # else:
    #     form = SymptomInputForm()

    # return render(request,'.html',{"token":"9873216879"}))
    return render(request,'recommend/symptominput.html')

    

#증상선택
def symptom_choice(request):
    return render(request,'recommend/symptomchoice.html')

# # 진료과목 확인
# def check_dpt(request):
#     return render(request,'recommend/symptominput.html')
############################################

#주소입력: 실시간 위치 받은 후 (js to html 탬플릿으로 데이터 전달) 탬플릿으로 데이터 받는다
#확인을 누르면 최종 좌표값이 post방식으로 input태그에 담겨서 추천 병원(recommend_hos) 쪽으로 전달
def addr_input(request):

    # 임의의 과 설정
    rec_dpt = '정형외과'

    data = []
    cols = ['rec_dpt']
    rows = []

    rows.append(rec_dpt)
    tmp = dict(zip(cols,rows))
    data.append(tmp)
    data = json.dumps(data)
    return render(request,'recommend/addrinput.html',{'datas':data})

#추천병원
#addr_input에서 확인버튼이 rec_hos함수를 호출함
#if method=='post'면 위경도가 같이 전달: request.POST.get(‘lat’) request.POST.get(‘lng’)
#위경도를 변수에 튜플형식으로 넣어줌
#위경도 튜플로 haversine 라이브러리 이용해 거리 계산
#request.POST.get(‘dpt’)
#models.py>class HospitalInfo 가져오기(db)
#filter(장고내부기능)걸어서 가져온 dpt와 medicourse contains(method)통해 해당과의 병원리스트만 가져옴
#일정거리 내에 병원 계산:for문
@csrf_exempt 
def recommend_hos(request):
    if request.method == "POST":
        
        # 임의의 과 설정
        
        post_info = request.POST.get('info')
        info_list = post_info.split(',')

        # 사용자 위경도
        usr_lat = float(info_list[0])
        usr_lng = float(info_list[1])
        
        # 사용자 거주동
        usr_dong = []
        for info in info_list[2].split(' ') :
            if "동" in info :
                usr_dong.append(info)

        # 사용자 거주시
        usr_sigun = []
        for info in info_list[2].split(' ') :
            if "시" in info :
                usr_sigun.append(info)

        # 사용자가 추천받은과
        rec_dpt = info_list[3]

        
        ##임의의 동이름 설정
        usr_dong[0] = '중동'
        usr_sigun[0] = '부천시'

        # DB에서 원하는 병원리스트 뽑아오기
        # hos_db = HospitalInfo.objects.filter(medi_course__contains=rec_dpt and medi_course__contains=usr_dong[0])
        # 추천과에 맞는 리스트
        criterion1 = Q(medi_course__contains=rec_dpt)
        # 내위치에 맞는 리스트
        criterion2 = Q(addr__contains=usr_dong[0])
        criterion3 = Q(addr__contains=usr_sigun[0])
        # 추천과 and 위치 만족하는 DB 행들의 모임
        hos_db = HospitalInfo.objects.filter(criterion1 & criterion2 & criterion3)

        cols = ['hos_id','hos_name','dist','hos_lat','hos_lng','rec_dpt','usr_lat','usr_lng']
        data = []
        for hos in hos_db:
            rows = []
            # 내 위치 위경도
            my_tus = (usr_lat,usr_lng)
            hos_tus = (float(hos.latitude),float(hos.longitude))

            # 직선거리
            dist = round(haversine(my_tus,hos_tus, unit='m'))

            rows.append(hos.hos_id)
            rows.append(hos.hos_name)
            rows.append(dist)
            rows.append(hos.latitude)
            rows.append(hos.longitude)
            rows.append(rec_dpt)
            rows.append(usr_lat)
            rows.append(usr_lng)

            tmp = dict(zip(cols,rows))
            data.append(tmp)

        data = json.dumps(data,ensure_ascii=False)
        # 판다스로 거리 오름차순 정렬
        # pd_data = pd.DataFrame(data).sort_values("dist")
        # print(pd_data)
        
        return render(request,'recommend/hoslist.html',{'datas':data})
    else :
        print("get")
    return render(request,'recommend/hoslist.html')

#병원별 정보제공
#hos_info,hos_info_detail 두 테이블 hos_id로 join ->테이블 변수로 저장(queryset) render의 3번째 파라미터에 담아 탬플릿으로 전달
#template파일에 데이터 넣어줌

def hos_info(request,get_param,param):

    data = HospitalInfo.objects.filter(hos_id=param)
    # 추천과 
    get_param = get_param.split('&')
    dpt = get_param[0]
    # 사용자 위경도
    usr_lat = float(get_param[1])
    usr_lng = float(get_param[2])

    
    return render(request,'recommend/hosinfo.html',{'datas':data,'dpt':dpt,'usr_lat':usr_lat,'usr_lng':usr_lng})

# #주변 병원 지도 표현  
# def get_hos_map(request):
#     return render(request,'recommend/symptominput.html')

#병원 기록 저장
def save_hos_info(request):
    return render(request,'recommend/hos_save.html')

