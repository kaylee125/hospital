import json
import requests
from bs4 import BeautifulSoup
import re
from infra.spark_session import get_spark_session
from infra.util import cal_std_day
from pyspark.sql.types import *
from pyspark.sql.functions import col
from infra.hdfs_client import get_client


class KakaoMap:
    READ_DIR='/hospital_code/hospital_code2022-10-29 (1).csv'
    FILE_DIR='/kakao_hos_info/'
    # FILE_NAME='kakaomap'+cal_std_day(0)+'.json'
    BASE_URL='https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&sq=&o=&q='
    

    @classmethod
    def extract_data(cls):
        #병원데이터에서 전화번호만 추출
        df = get_spark_session().read.csv(cls.READ_DIR, encoding='cp949', header=True)
        # sigungu_list=list(df.select(col('시군명')).distinct().toPandas())
        # print(sigungu_list)
      
        new_df=df[df['통합영업상태명']=='영업/정상']
        tel=new_df.select('소재지시설전화번호')
        tel_list=list(tel.toPandas()['소재지시설전화번호'])
        # print(len(tel_list)) #15653

        #리스트 분할함수
        #나누고 싶은 리스트와 몇개씩 분할 할것인지만 넣어주면, 원하는 길이로 리스트를 나눠서 하나의 리스트로 묶어 반환
        def list_chunk(lst, n):
            return [lst[i:i+n] for i in range(0, len(lst), n)]

        list_chunked = list_chunk(tel_list, 500)
        # print(len(list_chunked))
        num=2

        #분할한 리스트 하나씩 반복
        for tel_no in list_chunked[3:]:

            kakao_url=[]
            data=[]
            num=num+1

            ####다음에 전화번호로 병원 검색->카카오맵 접속 링크 구하기
            for i in tel_no:
                try:
                    #파일명 지정
                    cls.FILE_NAME   = str(num)+'kakao_hos_info'+cal_std_day(0)+'.json'
                    daum_res        = requests.get(cls.BASE_URL+i)
                    d_soup          = BeautifulSoup(daum_res.content,'lxml')
                        
                except:
                    continue
                
                try:
                    s1=d_soup.find('div',{'class':'pannel'}).find('li')
                    link=s1.find('a')['href']
                    #문자열+숫자 중에서 숫자만 빼오기
                    numbers = re.sub(r'[^0-9]', '', link)
                    print(numbers)
                    #카카오 url 추출
                    kakao_url.append('https://place.map.kakao.com/m/main/v/'+numbers)
                    
                except:
                    pass

            #####카카오맵 접속링크로 하나씩 접속해서 정보 크롤링
            print('카카오맵 링크 추출시작')
            for i in kakao_url:
                row=[]
                #카카오맵 url호출 및 json 저장
                kakao_res=requests.get(i)
                k_json=kakao_res.json()

                #병원명
                try:
                    hospital_name=k_json['basicInfo']['placenamefull']
                    row.append(hospital_name)

                except:
                    continue
                #전화번호
                try:
                    phonenum=k_json['basicInfo']['phonenum']
                    row.append(phonenum)
                except:
                    row.append(None)

                #의사 수 
                doc_num_arr=[]
                try:
                    doc_num_arr.append(k_json['hospitalInfo']['list'][0]['infoList'][1]['desc2'])
                    row.append(doc_num_arr)
                except:
                    row.append(None)
                
                #진료정보
                opentime_info=[]
                try:
                    opentime_info.append(k_json['hospitalInfo']['list'][1]['openHourList'])
                    row.append(opentime_info)
                except:
                    row.append(None)

                #별점
                try:
                    feedback=k_json['basicInfo']['feedback']['scoresum']/k_json['basicInfo']['feedback']['scorecnt']
                    row.append(feedback)
                except:
                    row.append(0)
                
                #리뷰 텍스트
                try:
                    r_cnt=len(k_json['comment']['list'])
                    review_txt_in_arr=[]
                    for j in range(r_cnt) :
                        review_txt_in_arr.append(k_json['comment']['list'][j]['contents'])
                    row.append(review_txt_in_arr)
                except:
                    row.append(None)

                #############################################
                cols=['병원명','전화번호','의사 수 ','진료정보','별점','리뷰텍스트']
                tmp = dict(zip(cols,row))
                data.append(tmp)

            get_client().write(cls.FILE_DIR+cls.FILE_NAME,json.dumps(data,ensure_ascii=False),overwrite=True,encoding='utf-8')
            # print(tel_no+'추출완료')





            #진료과목
            # depart_cnt=len(k_json['hospitalInfo']['list'][0]['subjectList'])
            # depart_in_arr=[]
            # try:
            #     for k in range(depart_cnt):
            #         depart_in_arr.append(k_json['hospitalInfo']['list'][0]['subjectList'][k]['name'])
            #     row.append(depart_in_arr)
            # except:
            #     row.append('-')

            #  #장치종류
            # device_cnt=len(k_json['hospitalInfo']['list'][0]['deviceList'])
            # device_arr=[]
            # try:
            #     for k in range(device_cnt):
            #         depart_in_arr.append(k_json['hospitalInfo']['list'][0]['deviceList'][k]['name'])
            #     row.append(device_arr)
            # except:
            #     row.append('-')
