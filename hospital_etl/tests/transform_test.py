"""
This file demonstrates common uses for the Python unittest module
https://docs.python.org/3/library/unittest.html
"""
import unittest

from datajob.transform.hospital_code import HospitalCode
from datajob.transform.kakaomap import KakaoMap
from datajob.transform.for_web import WebSiteUploader
# from datajob.transform.local_code import LocalCodeTransformer

class MTest(unittest.TestCase):


    def test1(self):
        HospitalCode.transform_data()

    def test2(self):
        KakaoMap.transform_data()

    def test3(self):
        WebSiteUploader.upload()


    # def test3(self):
    #     LocalCodeTransformer.transform()


if __name__ == '__main__':
    unittest.main()
