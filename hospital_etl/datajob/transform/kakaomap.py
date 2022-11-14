import json
import requests
from bs4 import BeautifulSoup
import re
from infra.jdbc import DataWarehouse,save_data
from infra.spark_session import get_spark_session
from infra.util import cal_std_day
from pyspark.sql.types import *
from pyspark.sql.functions import col
from pyspark.sql import Row
from infra.hdfs_client import get_client


class KakaoMap:
    BASE_DIR='/kakao_hos_info/'
    # SUB_DIR='kakao_hos_info2022-11-02.json'
    @classmethod
    def listToString(str_list):
        result = ""
        for s in str_list:
            result += s + " "
        return result.strip()


    @classmethod
    def transform_data(cls):
        # for n in range(1,33):

        # sub_dir=str(n)+'kakao_hos_info2022-11-04.json'  
        sub_dir='1kakao_hos_info2022-11-04.json'  
        file_dir= cls.BASE_DIR+sub_dir
        df=get_spark_session().read.json(file_dir, encoding='UTF-8').collect()
        df1=get_spark_session().read.json(file_dir, encoding='UTF-8')
        # print(df1.select(df1.진료정보).toLocalIterator())
        
        #진료정보 row값 하나의 str객체로 합치기


        info_df_list=df[0]['진료정보'][0]
        tel_df_list=df[0]['전화번호']

        info_list=[]
        temp_rows = []

        for i, e in enumerate(df):
            row_data = df[i]

            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', row_data)

            if not row_data['진료정보']:
                info_list.append('진료정보가 없습니다')
                temp_rows.append(Row(전화번호=row_data['전화번호'], 진료정보=info_text))
                continue

            for e in row_data['진료정보'][0]:
                val=e.day+':'+e.time
                info_list.append(val)

            info_text='/'.join(info_list)
            temp_rows.append(Row(전화번호=row_data['전화번호'], 진료정보=info_text))

        temp_df = get_spark_session().createDataFrame(temp_rows)
        df1 = df1.drop('진료정보')
        res_df = df1.join(temp_df, on='전화번호')
        res_df.show(3)








        # pandas_df1 = df1.to_pandas_on_spark()
        

           
            # kakao_df=df.select(col('병원명').alias('hos_name'),col('전화번호').alias('tel'),col('의사 수 ').alias('num_docs'),
            # col('진료정보').alias('open_info'),col('별점').alias('score').cast('float'),col('리뷰텍스트').alias('reviews'))


            # kakao_df.show()
            # save_data(DataWarehouse,kakao_df,'HOSPITAL_INFO_DETAIL')
            # print(n+'번째 파일 DW 업데이트 완료')

