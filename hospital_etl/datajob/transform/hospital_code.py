
import json
import requests
from bs4 import BeautifulSoup
import re
from infra.jdbc import DataWareHouse, save_data
from infra.spark_session import get_spark_session
from infra.util import cal_std_day
from pyspark.sql.functions import col, monotonically_increasing_id, row_number
from pyspark.sql.window import Window
# from pyspark.sql.DataFrame import *
import traceback
from pyspark.sql.types import *
from infra.hdfs_client import get_client
from infra.logger import get_logger

class HospitalCode:

    READ_DIR='/hospital_code/hospital_code2022-10-29.csv'
    @classmethod
    def transform_data(cls):
        #정상영업중인 병원리스트
        df = get_spark_session().read.csv(cls.READ_DIR, encoding='cp949', header=True)
        new_df=df[df['통합영업상태명']=='영업/정상']
        
        try:
            new_df = new_df.withColumn('HOS_ID', row_number().over(Window.orderBy(monotonically_increasing_id())))

            #전화번호  NULL값 제거,TEL컬럼을 PRIMARY KEY로 지정
            new_df=new_df.select(col('HOS_ID').cast('int'),col('사업장명').alias('HOS_NAME'),col('통합영업상태명').alias('STATUS'),col('업태구분명정보').alias('HOS_TYPE'),col('진료과목내용정보').alias('MEDI_COURSE'),col('소재지도로명주소').alias('ADDR'),col('소재지우편번호').alias('POST_CODE'),col('경도').alias('LONGITUDE').cast('float'),col('위도').alias('LATITUDE').cast('float'),col('소재지시설전화번호').alias('TEL'),col('시군코드').alias('SIDO_ID'))

            # save_data(DataWareHouse,new_df,'HOSPITAL_INFO_DETAIL')
            save_data(DataWareHouse, new_df, 'HOSPITAL_INFO')
            
        except Exception as e:
            traceback.print_exc()
            log_dict = cls.__create_log_dict(cal_std_day(0))
            cls.__dump_log(log_dict, e)
            
       

        

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

    
    
  