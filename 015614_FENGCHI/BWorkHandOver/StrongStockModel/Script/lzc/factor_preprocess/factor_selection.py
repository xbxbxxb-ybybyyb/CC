# @Time : 2020/12/7 14:29
# @Author : Zhichen Lu
# @File : factor_selection.py

import pandas as pd
from sklearn.feature_selection import SelectKBest
from conf.path_config import root_path

feature_address = '/data/group/800319/junkData/StrongStock/processed_factor_all_pool_by_date/ts_norm_%d/'%40
sample = pd.read_hdf(feature_address+'20150309.h5','20150309')
factor_evaluation = pd.read_excel(root_path+'/external_data/Fix样本内.xlsx',index_col=0)
inter_col = list(set(factor_evaluation.index).intersection(set(sample.columns)))

for num in range(400,800):
    factor_list = {}
    for eval_indicator in ['ic_all_t','ic_all_c','ic_all_d']:
        factor_list[eval_indicator] = factor_evaluation.loc[inter_col,eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:num]
    factor_num = len(set(factor_list['ic_all_t']).intersection(set(factor_list['ic_all_c'])).intersection(set(factor_list['ic_all_d'])))
    if factor_num>=400:
        print(factor_num)
        break

len(set(factor_list['ic_all_t']).union(set(factor_list['ic_all_c'])).union(set(factor_list['ic_all_d'])))
len(set(factor_list['ic_all_t']).intersection(set(factor_list['ic_all_c'])).intersection(set(factor_list['ic_all_d'])))
