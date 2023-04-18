"""
This file demonstrates common uses for the Python unittest module
https://docs.python.org/3/library/unittest.html
"""
import unittest

from datajob.extract.naver_jisik import NaverJisikExtractor
from datajob.extract.kakaomap_extract import KakaoMap



class MTest(unittest.TestCase):

    def test1(self):
        NaverJisikExtractor.extract_data()
    def test2(self):
        KakaoMap.extract_data()


if __name__ == '__main__':
    unittest.main()
