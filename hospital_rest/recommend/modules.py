import pandas as pd
import numpy as np
import random
from collections import Counter
from konlpy.tag import Okt
import joblib
from lightgbm import LGBMClassifier
# 불용어 사전
def return_stops():
    f_total = open('학습자연어_불용어/통합불용어진행중_원.txt','r',encoding='UTF-8').read()
    first_out = f_total.split('\n')
    stop_words = set(first_out)

    f = open('학습자연어_불용어/불용어모음집.txt','rt',encoding='UTF-8').read()
    tets= f.split('\n')[1:]
    stopwords = set(tets)
    return stop_words, stopwords

# 표제어 지정함수
def return_text_replaced(x):
    for i in range(len(x)):
        if x[i] == '속이':
            x[i] = '속'
        if x[i] == '남성':
            x[i] = '남자'
        if x[i] == '자꾸':
            x[i] = '자주'
        if x[i] == '박다':
            x[i] = '부딪히다'
        if x[i] == '포경':
            x[i] = '포경수술'
        if x[i] == '냉이':
            x[i] = '냉'
    return x

def return_X():
    df_20 = pd.read_csv('모델링테이블.csv',index_col=0)  # 텍스트만 가져와서 파일로 저장 후 쓰기 #
    X = df_20.drop('진료과', axis=1)
    return X

# 모델
gbm_pickle = joblib.load('lgb.pkl')

# 피처
def return_features():
    feats = pd.read_csv('feats.csv',index_col=0)
    feats = feats.values
    return feats


# 예측
# 명사 형용사 동사 추출
def input_text(text): # 장고랑 같이 연결해서 함수이름 확인하기
    okt = Okt()
    line = []

    line = okt.pos(text)

    test_adj = []
    stop_words = return_stops()[0]
    stopwords = return_stops()[1]

    test_adj = [word for word, tag in line if tag in ['Noun', 'Adjective', 'Verb'] and len(word) > 1]
    test_adj = [word for word in test_adj if not word in stop_words]
    test_adj = [word for word in test_adj if not word in stopwords]
    test_adj = return_text_replaced(test_adj)
    input_list = []
    X = return_X()
    for i in range(len(X.columns)):
        list_i = []
        input_list.append(list_i)

        # 표제화
    morphs_ques_word = []
    for i in test_adj:
        morphs_ques_word.append(okt.morphs(i, stem=True)[0])

    # 질문 내에서 피처의 개수 추출
    for j, k in enumerate(input_list):
        k = k.append(morphs_ques_word.count(pd.DataFrame(X.columns)[0].unique()[j]))
    return input_list

# 결과 추출 STEP 1
def return_result(x): # view에서 
    # boxes = []
    feat_out = []
    nonnull = []
    text = []
    X = return_X()
    feats = return_features()
    for i in range(len(input_list)):
        if input_list[i][0] != 0:
            text.append(X.columns[i])
    # input_lists에서 0 이 아닌 것의 텍스트를 가져오기

    for i in range(len(feats)):
        if text in feats[i]:
            feat_out.append(feats[i])
    apeen = []
    for i in feat_out:
        for j in i:
            apeen.append(j)
    tfidf_lists = list(set(apeen))

    if '0' in tfidf_lists:
        tfidf_lists.remove('0')             # 질문내보내는거랑 분리 

    ou = [X.columns.tolist().index(i) for i in tfidf_lists]

    random.shuffle(ou)
    indexes = random.sample(ou, 6)
    for i in range(len(input_list)):
        if input_list[i][0] != 0:
            nonnull.append(i)
    for i in indexes:
        if i in nonnull:
            indexes.remove(i)
    cols = X.columns[indexes] #########
    return cols 
    # print('해당 하는 증상이나 증상의 부위가 있다면 체크해주세요. 1 로')
    ### view에서 처리 
    # for i in cols:
    #     userinput = int(input('%s' % (i)))
    #     if userinput == 1:
    #         boxes.append(1)
    #     else:
    #         boxes.append(0)

    # return boxes, cols # view에서 boxes값이 오는거임 



# 결과 추출 STEP 2

def outputs(lists):
    X = return_X()
    if np.sum(lists) == 1: #피처 더 선택하는 페이지로 리디렉트
        result = return_result(lists)

        # input_list = pd.DataFrame(lists)
        # input_list = input_list.T
        # input_list.columns = X.columns
        # for i in result[1]:
        #     for j in range(len(result[0])):
        #         input_list[input_list.columns[input_list.columns.get_loc(i)]] = result[0][j]
        # lgb_pred = gbm_pickle.predict(input_list)
        # return lgb_pred[0]

        # 선택지 6 개 골르는 함수만 호출해서 값 같이 리턴해줘야함
        return result '항목 고르는 페이지로 리턴이되어야함' # view에서 처리 + 추출한피처 클라이언트쪽으로 전송 후 다시 받아야함 (기존피처가 유지되어야함 )
    elif np.sum(lists) == 0 :
        # return_require_inputs(lists)   # 사용자가 증상을 입력하는 페이지로 리 디렉트
        return '사용자가 다시 작성하게하는 페이지로 리턴' # view에서 처리 

    else:
        input_list = pd.DataFrame(lists)
        input_list = input_list.T
        input_list.columns = X.columns
        lgb_pred = gbm_pickle.predict(input_list)
        return lgb_pred[0]


# 1차 분류 0으로 된 경우 다시 작성 요구
# def return_require_inputs(lists):
#     text = input('증상을 입력해보세요 : ')
#     input_list = input_text(text)
#     result = outputs(input_list)
#     return result


# 예측값 추출
# text 은 html에서 전송받아서 넣기
def resluts(text):
    # text = input('증상을 입력해보세요 : ') # 먼저 text 넘겨받고  
    if # 문장일때
 
        text = input_text(text) # 문장으로 들어올때만 # 타입이 달라짐
    # type이 문자열이면 리스트로바꿔서 
    result = outputs(text)
    return result


# 예측불러오기 

# resluts()

# 웹서버에 끼워넣고 



