# coding: utf-8
# Author：fengchi863
# Date ：2023/9/8 9:50

root_path = '/data/user/015614/TEST/active_concept_test/'

CONCEPT_ACTIVE_SHIFT_DAYS = 10  # 对于概念，过去10日内活跃过即算作当前活跃

BIG_CONCEPT_RANGE = (50, 100)   # 划分大板块、中板块、小版块，以成分股数量来定，左闭右开
MID_CONCEPT_RANGE = (10, 50)
SML_CONCEPT_RANGE = (1, 10)

BIG_CONCEPT_PCT = 0.015
MID_CONCEPT_PCT = 0.025
SML_CONCEPT_PCT = 0.035

BIG_CONCEPT_EXCESS_PCT = 0.0
MID_CONCEPT_EXCESS_PCT = 0.005
SML_CONCEPT_EXCESS_PCT = 0.01