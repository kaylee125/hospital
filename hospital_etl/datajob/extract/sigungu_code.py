import json
import time
import pandas as pd
from bs4 import BeautifulSoup
from infra.hdfs_client import get_client
from infra.logger import get_logger
from infra.util import execute_rest_api


class LocalCode:
    URL = 'http://apis.data.go.kr/1741000/StanReginCd/getStanReginCdList'
    SERVICE_KEY = 'NvoJpM4nyxzXkb5F8hffSDHLrfuCyIcVBqBSDCgTa+/7CtQnsrFwE8y/a0lLPVxN1AESAPkiMkfoS7KYrck13A=='
    MAX_PAGE_NO = 21

    @classmethod
    def extract_data(cls):
        params = cls.__create_params()
        # <totalcount>20550</totalcount> : 총 20550개의 item
        # 최대 numofrows = 1000
        # pageno -> 21페이지
        data = []
        for page_no in range(1, cls.MAX_PAGE_NO + 1):
            try:
                # set params
                params['pageNo'] = str(page_no)
                params['numOfRows'] = '1000'
                # execute rest api
                res = execute_rest_api('get', cls.URL, {}, params)
                # parse and save data
                cls.__parse_and_save_data(data, res)

                print(page_no, len(data))
                cls.__write_to_csv(data)
            except Exception as e:
                log_dict = cls.__create_log_dict(params)
                cls.__dump_log(log_dict, e)
                raise e

    # 추출한 데이터를 csv파일로 저장하는 함수
    @classmethod
    def __write_to_csv(cls, data):
        # write to csv file
        df = pd.DataFrame(data)
        with get_client().write('/hospital_code/local_code/local_code.csv', overwrite=True, encoding='CP949') as writer:
            df.to_csv(writer, header=['지역코드', '시도코드', '시군구코드',  '읍면동코드', '리코드', '지역주소명',
                '상위지역코드', '최하위지역명'], index=False)

    # bs이용해서 파싱한 후 데이터에 삽입하는 함수
    @classmethod
    def __parse_and_save_data(cls, data, res):
        # get data from tag
        soup = BeautifulSoup(res, 'html.parser')
        region_cds = soup.findAll('region_cd')
        sido_cds = soup.findAll('sido_cd')
        sgg_cds = soup.findAll('sgg_cd')
        umd_cds = soup.findAll('umd_cd')
        ri_cds = soup.findAll('ri_cd')
        locatadd_nms = soup.findAll('locatadd_nm')
        locathigh_cds = soup.findAll('locathigh_cd')
        locallow_nms = soup.findAll('locallow_nm')

        time.sleep(1)

        # construct list and append to datalist
        for i in range(len(region_cds)):
            data.append([region_cds[i].text, sido_cds[i].text, sgg_cds[i].text, umd_cds[i].text, ri_cds[i].text,
                            locatadd_nms[i].text, locathigh_cds[i].text, locallow_nms[i].text])

    # 파라미터 생성
    @classmethod
    def __create_params(cls):
        params = {'serviceKey': cls.SERVICE_KEY,
                'pageNo': '1',
                'numOfRows': '1000',
                'type': 'xml'
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