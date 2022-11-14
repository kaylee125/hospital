from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from recommend.modules import inputs
from haversine import haversine
from recommend.models import HospitalInfo, RecHistory, AuthUser, UserHistory
from django.db.models import Q
import pandas as pd
import json
from datetime import date
from accounts.forms import UserForm
from django.contrib.auth import authenticate,login

# Create your views here.


#증상입력: 텍스트로 입력 받고 모델결과 확인해서 결과가 잘 나오면 check_dpt로 render 안나오면 symptom_choice로 render
def symptom_input(request):
    # if request.method=='POST':
    #     symptomtext=request.POST.get('symptomtext')
    #     rec_dpt=inputs(symptomtext,1)
        
    #     return render(request,'recommend/symptominput.html',{'data':rec_dpt})
    return render(request,'recommend/symptominput.html')
   
    # if request.method=='POST':
    #     #모델 호출
    #     input_text(입력값)
    #     if 피쳐개수==0:
    #         return redirect('/')
    #     elif 피쳐개수==1:
    #         return render(symptom_choice로 보내기)
    #     else:
    #         return render(request,'recommend/addrinput.html')

    # else:


#증상선택
def symptom_choice(request):
    symptom_list = request.POST.getlist('symptom_selected')
    symptomtext = ' '.join(symptom_list)
    rec_dpt=inputs(symptomtext,1)

    #모듈호출
    return render(request,'recommend/symptomchoice.html')

# 진료과목 확인
def check_dpt(request):
    if (request.method == "POST") & (type(request.POST.get('symptomtext')) is str ):
        symptomtext=request.POST.get('symptomtext')
        rec_dpt=inputs(symptomtext,1)

        
        
        # 추천과가 나온 경우
        if type(rec_dpt) is str :
            # 임의의 과 설정
            # rec_dpt = '정형외과'

            #db저장:symptomtext,rec_dpt
            if request.user.is_authenticated:

                rec_his=UserHistory()
                rec_his.symptominput=symptomtext
                rec_his.rec_dpt=rec_dpt

                user_info = AuthUser.objects.filter(username = request.user)[0]
                rec_his.username = user_info
                input_date=date.today()
                rec_his.input_date=input_date.isoformat()
                rec_his.save()

                
                data = []
                cols = ['rec_dpt']
                rows = []
                rows.append(rec_dpt)
                tmp = dict(zip(cols,rows))
                data.append(tmp)
                data = json.dumps(data,ensure_ascii=False)
                return render(request,'recommend/addrinput.html',{'datas':data})


            data = []
            cols = ['rec_dpt']
            rows = []

            rows.append(rec_dpt)
            tmp = dict(zip(cols,rows))
            data.append(tmp)
            data = json.dumps(data,ensure_ascii=False)
            return render(request,'recommend/addrinput.html',{'datas':data})

        # 증상입력을 다시 해야하는 경우
        # 이 경우 사용자의 인풋에서 피쳐가 하나도 나오지 않았기 때문에 다시 입력을 받을 필요가 있다.
        # 그런 경우에는 사용자에게 안내를 해줘야 한다.
        elif rec_dpt == 0 :
            warn_text = '결과가 나오지 않았습니다. 조금만 더 자세하게 부탁드려요!'
           
            data = []
            cols = ['usr_input','result','warn_text']
            rows = []

            rows.append(symptomtext)
            rows.append(rec_dpt)
            rows.append(warn_text)
            tmp = dict(zip(cols,rows))
            data.append(tmp)
            data = json.dumps(data,ensure_ascii=False)
            return render(request,'recommend/symptominput.html',{'datas':data} )
            # return redirect('/recommend/symptominput')
        # 피쳐 선정으로 가야 하는 경우
        elif type(rec_dpt) is list :

            fix_feature = rec_dpt[-1]
            choice = rec_dpt[:10]
            print(fix_feature,choice)
            return render(request,'recommend/symptomchoice.html',{'datas':choice,'fix_feature':fix_feature,'symptomtext_origin':symptomtext})

    elif (request.method == "POST") & (type(request.POST.getlist('symptom_selected')) is list ) :
        symptomtext_origin = request.POST.get('symptomtext_origin')
        symptom_list = request.POST.getlist('symptom_selected')
        # 사용자가 선택항목에서 아무것도 선택하지 않고 진료과목 확인 클릭한 경우 다시 선택하게끔 하는 코드
        # 이 경우 사용자에게 선택하지 않았음을 경고 해줘야 한다.
        if len(symptom_list)==0  :
            warn_text='아무것도 선택하지 않았습니다. 최소 1개 이상 선택 해야 합니다.'
            fix_feature=request.POST.get('fix_feature')
            symptom_retry=request.POST.get('symtpom_retry')
            symptom_retry=symptom_retry.replace(']','').replace('[','').replace("'",'').split(',')
            return render(request,'recommend/symptomchoice.html',{'datas':symptom_retry,'fix_feature':fix_feature,'warn_text':warn_text})
        else:

            fix_feature =request.POST.get('fix_feature')
            symptom_list.append(fix_feature)
            symptomtext = ' '.join(symptom_list)
            rec_dpt=inputs(symptomtext,1)

            #db저장
            if request.user.is_authenticated:

                rec_his=UserHistory()
                rec_his.select_symptom= ' '.join(symptom_list[:-1])
                rec_his.rec_dpt=rec_dpt
                rec_his.symptominput = symptomtext_origin
                user_info = AuthUser.objects.filter(username = request.user)[0]
                rec_his.username = user_info
                input_date=date.today()
                rec_his.input_date=input_date.isoformat()
                rec_his.save()
                
                data = []
                cols = ['rec_dpt']
                rows = []

                rows.append(rec_dpt)
                tmp = dict(zip(cols,rows))
                data.append(tmp)
                data = json.dumps(data,ensure_ascii=False)
                return render(request,'recommend/addrinput.html',{'datas':data})
            

            data = []
            cols = ['rec_dpt']
            rows = []

            rows.append(rec_dpt)
            tmp = dict(zip(cols,rows))
            data.append(tmp)
            data = json.dumps(data,ensure_ascii=False)
            return render(request,'recommend/addrinput.html',{'datas':data})
            


############################################

#주소입력: 실시간 위치 받은 후 (js to html 탬플릿으로 데이터 전달) 탬플릿으로 데이터 받는다
#확인을 누르면 최종 좌표값이 post방식으로 input태그에 담겨서 추천 병원(recommend_hos) 쪽으로 전달
def addr_input(request):
 
    return render(request,'recommend/addrinput.html')
    

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
        # 사용자 위경도
        usr_lat = float(request.POST.get('usr_lat'))
        usr_lng = float(request.POST.get('usr_lng'))
    
        # 사용자가 추천받은과
        rec_dpt = request.POST.get('rec_dpt')

        # 사용자가 선택한 반경

        usr_dist = int(request.POST.get('usr_dist').replace('km','').replace('m',''))
        # 100보다 작으면 km로 계산해야한다.
        if usr_dist < 100 :
            usr_dist = usr_dist*1000
        elif usr_dist == '':
            usr_dist = 2000



        
        ##임의의 동이름 설정

        # DB에서 원하는 병원리스트 뽑아오기
        # hos_db = HospitalInfo.objects.filter(medi_course__contains=rec_dpt and medi_course__contains=usr_dong[0])
        # 추천과에 맞는 리스트
        criterion1 = Q(medi_course__contains=rec_dpt)
        # 위경도가 null 이 아닌 리스트
        criterion2 = Q(longitude__isnull=False)
        # 추천과 and 위치 만족하는 DB 행들의 모임
        hos_db = HospitalInfo.objects.filter(criterion1 & criterion2)

        cols = ['hos_id','hos_name','dist','hos_lat','hos_lng','rec_dpt','usr_lat','usr_lng']
        data = []
        for hos in hos_db:
            rows = []
            # 내 위치 위경도
            my_tus = (usr_lat,usr_lng)

            # 병원에 위경도가 등록되어있지 않은경우..
            hos_tus = (float(hos.latitude),float(hos.longitude))

            # 직선거리
            dist = round(haversine(my_tus,hos_tus, unit='m'))
            if dist < usr_dist :

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
        if json.loads(data) == [] :
            data = {"rec_dpt":rec_dpt,"usr_lat":usr_lat,"usr_lng":usr_lng}
            data = json.dumps(data,ensure_ascii=False)
        # 판다스로 거리 오름차순 정렬
        # pd_data = pd.DataFrame(data).sort_values("dist")

        
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