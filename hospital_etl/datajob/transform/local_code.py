# from infra.jdbc import DataWareHouse, save_data
# from infra.spark_session import get_spark_session
# from pyspark.sql.functions import col, split, monotonically_increasing_id, row_number
# from pyspark.sql.window import Window

# class LocalCodeTransformer:
#     FILE_NAME = '/hospital_code/local_code/local_code.csv'

#     @classmethod
#     def transform(cls):
#         df_local = get_spark_session().read.csv(cls.FILE_NAME, encoding='CP949', header=True)     
   
#         df_local = df_local.select(col('지역코드').substr(0, 5).alias('loc_code'), col('시도코드').alias('sido_code'), 
#                                     col('시군구코드').alias('sigungu_code'), split(col('지역주소명'), '[\s]', -1).alias('name'))

#         localnames = df_local.select('loc_code').collect()  # collect를 이용해 데이터프레임 한 열을 리스트로 생성
#         # 전체주소명데이터를 가공해서 시도, 시군구 리스트 각각에 집어넣음
#         sido_list = []
#         sigungu_list = []
#         for i in range(len(localnames)):
            


#         # 시도, 시군구 리스트를 데이터프레임으로 생성
#         sido_sigungu_list = zip(sido_list, sigungu_list)
#         columns = ["sido", "sigungu"]
#         df_localnames = get_spark_session().createDataFrame(data=sido_sigungu_list, schema=columns)
#         df_localnames.show(3)

#         # 두 데이터프레임을 합하기 위해서 두 DF에서 가상으로 idx만든다음, 그 idx로 join
#         df_local = df_local.withColumn('row_index', row_number().over(Window.orderBy(monotonically_increasing_id())))
#         df_localnames = df_localnames.withColumn('row_index', row_number().over(Window.orderBy(monotonically_increasing_id())))
#         df_local = df_local.join(df_localnames, on=["row_index"]).drop("row_index", "name")
#         df_local = df_local.distinct()

#         df_local.show()
#         print(df_local.count())
        
#         # DW에 저장
#         save_data(DataWareHouse, df_local, 'LOC')


#     # 시도, 시군구 리스트에 집어넣기
#     @classmethod
#     def __construct_list_sido_sigungu(cls, sido_list, sigungu_list, tmp):
#         if len(tmp) == 3:
#             sido_list.append(tmp[0])
#             sigungu_list.append(' '.join([tmp[1], tmp[2]]))
#         elif len(tmp) == 2:
#             sido_list.append(tmp[0])
#             sigungu_list.append(tmp[1])
#         elif len(tmp) == 1:
#             sido_list.append(tmp[0])
#             sigungu_list.append('')

