from datetime import datetime
import json
from bs4 import BeautifulSoup
from infra.spark_session import get_spark_session
from infra.util import cal_std_day, execute_rest_api
from infra.hdfs_client import get_client
from infra.logger import get_logger
import pandas as pd
from pandas import DataFrame
import requests
from io import StringIO

class HospitalCode:
    
    KEY='ecfbc592d2a441f9b2170a51efd15e15'
    FILE_DIR = '/hospital_code/'
    FILE_NAME = 'hospital_code'+ cal_std_day(0)
    BASE_URL = 'https://openapi.gg.go.kr/AsembyStus?'
    # PARAMS = {'KEY' : KEY,'Type':'json','pIndex':'1','pSize':'100'}
    MAX_PAGE_NO = 238
    #HEADERS = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}


    @classmethod
    def extract_data(cls):
        row=[]

        for page_no in range(1,cls.MAX_PAGE_NO+1):
            try:
                #set params
                params = cls.__create_params()
                params['pIndex']=str(page_no)
                params['pSize']='100'
                #api 호출
                response = requests.get(cls.BASE_URL,params)
                bs = BeautifulSoup(response.content, 'lxml')
                bs_str=bs.findAll('p')[0].text
                bs_dict = json.loads(bs_str.replace("'", "\"")) # json 모듈이 큰 따옴표만 인식하기 때문에 작은따옴표를 큰따옴표로 변환
                
                for n in range(1,100):
                    c=bs_dict['AsembyStus'][1:][0]['row'][n]
                    row.append(c)
                cls.__write_to_csv(row)

            except Exception as e:
                log_dict = cls.__create_log_dict(params)
                cls.__dump_log(log_dict, e)
                continue
    
        
    @classmethod
    def __write_to_csv(cls,row):
        df=pd.DataFrame(row)

        # df=df[['SIGUN_NM','LICENSG_DE','BIZPLC_NM','UNITY_BSN_STATE_NM','LOCPLC_FACLT_TELNO','REFINE_ROADNM_ADDR','REFINE_LOTNO_ADDR','REFINE_ZIP_CD','REFINE_WGS84_LAT','REFINE_WGS84_LOGT','BIZCOND_DIV_NM_INFO','TREAT_SBJECT_CONT','TREAT_SBJECT_CONT_INFO']]

        file_name = cls.FILE_DIR + cls.FILE_NAME +'.csv'
        with get_client().write(file_name, overwrite=True, encoding='cp949') as writer:
            df.to_csv(writer, index=False,header=['시군코드','시군명','인허가일자','인허가취소일자','영업상태구분코드','통합영업상태구분코드','통합영업상태명','영업상태명','폐업일자','휴업시작일자','휴업종료일자','재개업일자','소재지시설전화번호','소재지면적정보','사업장명','업태구분명정보','X좌표값','Y좌표값','의료기관종별명','의료인수','입원실수','병상수','총면적','진료과목내용','진료과목내용정보','지정취소일자','완화의료지정형태','완화의료담당부서명','특수구급차대수','일반구급차대수','총종업원수','구조사수','허가병상수','최초지정일자','소재지지번주소','소재지도로명주소','소재지우편번호','경도','위도'],encoding="cp949")

            
    
    @classmethod
    def __create_params(cls):
        params = {'KEY': cls.KEY,
                'Type': 'json',
                'pIndex': '1',
                'pSize': '100'
        }
        return params

    # 로그 dump
    @classmethod
    def __dump_log(cls, log_dict, e):
        log_dict['err_msg'] = e.__str__()
        log_json = json.dumps(log_dict, ensure_ascii=False)
        get_logger('corona_extractor').error(log_json)

    # 로그데이터 생성
    @classmethod
    def __create_log_dict(cls, params):
        log_dict = {"is_success": "Fail",
                    "type": "extract_local_code",
                    "params":params
        }
        return log_dict


