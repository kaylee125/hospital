import json
import requests
from bs4 import BeautifulSoup
import re
from infra.jdbc import DataWarehouse,save_data
from infra.spark_session import get_spark_session
from infra.util import cal_std_day
from pyspark.sql.types import *
from pyspark.sql.functions import col, approx_count_distinct
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
        
        total_df = get_spark_session().createDataFrame([], schema='TEL string, OPEN_INFO string, HOS_NAME string')
        except_df = get_spark_session().createDataFrame([], schema='TEL string, OPEN_INFO string, HOS_NAME string')

        for n in range(1,33):

            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', n)
            
            sub_dir=str(n)+'kakao_hos_info2022-11-04.json'   
            file_dir= cls.BASE_DIR+sub_dir
            df=get_spark_session().read.json(file_dir, encoding='UTF-8').collect()
            df1=get_spark_session().read.json(file_dir, encoding='UTF-8')
                        
            temp_rows = []

            for i, e in enumerate(df):
                info_list=[]
                row_data = df[i]

                if not row_data['진료정보']:
                    info_list.append('진료정보가 없습니다')
                    temp_rows.append(Row(전화번호=row_data['전화번호'], 진료정보=info_text))
                    continue

                for e in row_data['진료정보'][0]:
                    val=e.day+':'+e.time
                    info_list.append(val)

                info_text='/'.join(info_list)
                temp_rows.append(Row(전화번호=row_data['전화번호'], 진료정보=info_text))
                # print(temp_rows)

            temp_df = get_spark_session().createDataFrame(temp_rows)

            # temp_df.show(3)
            df1 = df1.drop('진료정보')
            res_df = df1.join(temp_df, on='전화번호')
            res_df = res_df.select(res_df.전화번호.alias('TEL'),res_df.진료정보.alias('OPEN_INFO'),res_df.병원명.alias('HOS_NAME'))
            total_df = total_df.union(res_df)
      
        total_df = total_df.distinct()
        save_data(DataWarehouse,total_df,'HOSPITAL_INFO_DETAIL')






        # pandas_df1 = df1.to_pandas_on_spark()
        

           
            # kakao_df=df.select(col('병원명').alias('hos_name'),col('전화번호').alias('tel'),col('의사 수 ').alias('num_docs'),
            # col('진료정보').alias('open_info'),col('별점').alias('score').cast('float'),col('리뷰텍스트').alias('reviews'))


            # kakao_df.show()
            # save_data(DataWarehouse,kakao_df,'HOSPITAL_INFO_DETAIL')
            # print(n+'번째 파일 DW 업데이트 완료')
