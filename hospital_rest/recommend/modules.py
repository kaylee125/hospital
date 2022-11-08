import pandas as pd
import numpy as np
from time import time
from collections import Counter
from konlpy.tag import Okt
import random
import joblib
# from joblib import dump, load
from lightgbm import LGBMClassifier
from hanspell import spell_checker
# 불용어사전
def return_stops():
    f_total = open('/home/worker/project/hospital_rest/recommend/학습자연어_불용어/통합불용어진행중_원.txt','r',encoding='UTF-8').read()
    first_out = f_total.split('\n')
    stop_words = set(first_out)

    f = open('/home/worker/project/hospital_rest/recommend/학습자연어_불용어/불용어모음집.txt','rt',encoding='UTF-8').read()
    tets= f.split('\n')[1:]
    stopwords = set(tets)
    return stop_words, stopwords

# 표제어 변환
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

# 컬럼들 가져오기(피처)
f = open('/home/worker/project/hospital_rest/recommend/x_cols.txt','r',encoding='UTF-8').read()
X_columns = f.split('\n')
X_columns = X_columns[:-1]



# 모델
gbm_pickle = joblib.load('/home/worker/project/hospital_rest/recommend/lgb.pkl')

# 각 진료과별 피처 array 형태

def return_features():
    feats = pd.read_csv('/home/worker/project/hospital_rest/recommend/feats.csv',index_col=0)
    feats = feats.values
    return feats


# 실제예측


# 텍스트 입력되면 모델된 피처에 해당하는지 안하는지 돌려주는 함수
def input_text(text):
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

    for i in range(len(X_columns)):
        list_i = []
        input_list.append(list_i)

        # 표제화
    morphs_ques_word = []
    for i in test_adj:
        morphs_ques_word.append(okt.morphs(i, stem=True)[0])

    # 질문 내에서 피처의 개수 추출
    for j, k in enumerate(input_list):
        k = k.append(morphs_ques_word.count(pd.DataFrame(X_columns)[0].unique()[j]))

    return input_list

# 들어온 문장이 피처 1개만 포함한다면 그 피처와 관련된 진료과목들의 피처들을
# 랜덤으로 뽑아서 6개만 리스트로 돌려주는 함수
# def return_question(input_list):
#     feat_out = []
#     nonnull = []
#     text= []
#     question_lists = []
#     apeen = []
#     feats = return_features()
#     for i in range(len(input_list)):
#         if input_list[i][0] != 0:
#             text.append(X_columns[i])
#     # input_lists에서 0 이 아닌 것의 텍스트를 가져오기

#     for i in range(len(feats)):
#         if text in feats[i]:
#             feat_out.append(feats[i])

#     for i in feat_out:
#         for j in i:
#             apeen.append(j)
#     tfidf_lists = list(set(apeen))

#     if '0' in tfidf_lists:
#         tfidf_lists.remove('0')

#     ou = [X_columns.index(i) for i in tfidf_lists]

#     random.shuffle(ou)
#     indexes = random.sample(ou, 6)
#     for i in range(len(input_list)):
#         if input_list[i][0] != 0:
#             nonnull.append(i)
#     for i in indexes:
#         if i in nonnull:
#             indexes.remove(i)
#     for i in indexes:
#         question_lists.append(X_columns[i])

#     return question_lists.append(X_columns[i])

def return_question(input_list):
    feat_out = []
    nonnull = []
    text= []
    question_lists = []
    apeen = []
    feats = return_features()
    for i in range(len(input_list)):
        if input_list[i][0] != 0:
            text.append(X_columns[i])
    # input_lists에서 0 이 아닌 것의 텍스트를 가져오기
    last_one = text
    for i in range(len(feats)):
        if text in feats[i]:
            feat_out.append(feats[i])

    for i in feat_out:
        for j in i:
            apeen.append(j)
    tfidf_lists = list(set(apeen))

    if '0' in tfidf_lists:
        tfidf_lists.remove('0')

    ou = [X_columns.index(i) for i in tfidf_lists]

    random.shuffle(ou)
    indexes = random.sample(ou, 6)
    for i in range(len(input_list)):
        if input_list[i][0] != 0:
            nonnull.append(i)
    for i in indexes:
        if i in nonnull:
            indexes.remove(i)
    for i in indexes:
        question_lists.append(X_columns[i])
        
    question_lists.append(last_one[0])
    
    return question_lists

# 들어오는 피처 갯수에 따라
# 피처 1이면 위에 return_question 써서 질문리스트 뽑아주는 함수사용해서 피처 6개불러와서 2차분류해주는 페이지에 반환해줘야함
# 피처 0 이면 예측수행할 수 없으니 다시 작성을 요구하는 페이지를 불러와줘야함
# 피처 2개 이상이면 예측 수행 하는 함수
def outputs(lists):
    if np.sum(lists) == 1:

        result = return_question(lists)
        return result 
        # 텍스트 7개 가져왔음 (리스트형태)
        # 7개 웹으로 보내야함   ##  symptomchoice 로

    elif np.sum(lists) == 0:
        return 0
    # 다시 작성하라고 요청해야함  ## symptominput 페이지에 작성 요구

    else:  # 피처갯수 제대로들어왔으니 예측수행 해서 웹에 돌려줘야함  ## addr 페이지에 표현

        input_list = pd.DataFrame(lists)
        input_list = input_list.T
        input_list.columns = X_columns
        lgb_pred = gbm_pickle.predict(input_list)

        return lgb_pred[0]

# 예시:::: 웹에서 가져오는 텍스트 임
# text = input('증상을 입력해보세요 : ')

# 들어온 text 형태에 따라 ??

def inputs(text,sel):

    if sel == 1:  # 문장이면:
        input_list = input_text(text)
        result_recommended = outputs(input_list)
        return result_recommended

    elif sel == 2 :  # 피처리스트이면?
        result = ''
        for i in text:
            result += '%s '%i
        input_list = input_text(result)
        result_recommended = outputs(input_list)
        return result_recommended
        

# 맞춤법검사
def gyojeong(text):
    try:
        result_train = spell_checker.check(text)
        text = result_train.as_dict()['checked']

    except:
        pass
    return text









