import json
import requests
from bs4 import BeautifulSoup
import re
from infra.jdbc import DataWareHouse, save_data
from infra.spark_session import get_spark_session
from infra.util import cal_std_day
from pyspark.sql.types import *
from pyspark.sql.functions import col
from infra.hdfs_client import get_client


class KakaoMap:
    BASE_DIR='/kakao_hos_info/'
    SUB_DIR='kakao_hos_info2022-11-02.json'


    @classmethod
    def transform_data(cls):
        for n in range(1,33):
            cls.SUB_DIR=str(n)+'kakao_hos_info2022-11-02.json'  
            file_dir= cls.BASE_DIR+ cls.SUB_DIR
            df=get_spark_session().read.json(file_dir, encoding='UTF-8')
            # df=get_spark_session().createDataFrame(data)

            kakao_df=df.select(col('병원명'),col('전화번호'),col('의사 수 '),col('진료정보'),col('별점').cast('float'),col('리뷰텍스트'))
            save_data(DataWareHouse,kakao_df,'HOSPITAL_INFO_DETAIL')
            print(n+'번째 파일 DW 업데이트 완료')

