from infra.jdbc import DataWarehouse, save_data, find_data, WebSite
from infra.spark_session import get_spark_session
from infra.util import cal_std_day
from pyspark.sql.functions import col
from pyspark.sql import Row



class WebSiteUploader:

    @classmethod
    def upload(cls):
        hos_info = find_data(DataWarehouse, "HOSPITAL_INFO")
        hos_info = hos_info.where(col("SIDO_ID").isNotNull())
        save_data(WebSite, hos_info.limit(int(hos_info.count())-1), "HOSPITAL_INFO")

    