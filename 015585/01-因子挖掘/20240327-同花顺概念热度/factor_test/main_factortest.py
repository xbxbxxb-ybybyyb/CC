# -*- coding: utf-8 -*-
# 测同花顺概念热度
import pandas as pd
import numpy as np
from itertools import product
import os
from run_factor_demo_parallel_new import run_factor
from test_factor_demo import strongFactorTest
from xquant.factordata import FactorData
import IO
import re
def get_corr_factor(df):
    r = ''
    for i in df.index:
        r = r+str(i)+':'+str(round(df.loc[i,'in_score'],2))+";"
    return r
print('开始同花顺概念热度因子测试')
start_date = '20160101'
end_date = '20191231'
res = pd.DataFrame(columns = ['IC','score','high_corr_factor','repeat_ratio'])
for factor_file in os.listdir('/dfs/user/015585/20240327-同花顺概念热度/factor/'):
    col = factor_file.replace('.h5','')
    print(col)
    def factor_test(start_date, end_date, IO, return_fillna_dic=False):
        if return_fillna_dic:
            # 返回因子为nan时的填充值
            return {col: 0, 'data': ['MD']}
        df_res = pd.read_hdf('/dfs/user/015585/20240327-同花顺概念热度/factor/' + factor_file)
        return df_res
    basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
    factor_path = '/dfs/user/015585/20240327-同花顺概念热度/factor_h5_final/'
    factor_df0 = run_factor(func=factor_test,
                            factor_name=col,
                            factor_type='T-1_factor',
                            start_date=int(start_date),
                            end_date=int(end_date),
                            basic_file_path=basic_file_path,
                            result_path=factor_path,
                            interval_res=False)
    df = pd.read_hdf(factor_path + col + '.h5')
    result_path = '/dfs/user/015585/20240327-同花顺概念热度/factor_report/'
    factor_test = strongFactorTest(int(start_date), int(end_date), cal_mi=None)
    factor_test.factor_test(df[[col]], result_path,
                            factor_corr_test=True, generate_pdf=False)
    check_score = factor_test.result_dic['check_score_res']
    res.loc[col,'IC'] = factor_test.result_dic['corr_sta'].loc['corr_tot', 'value']
    res.loc[col,'score'] = check_score.loc['score', 'tot_score']
    res.loc[col,'high_corr_factor'] = get_corr_factor(factor_test.result_dic['factor_corr_summary'])
    res.loc[col,'repeat_ratio'] = factor_test.result_dic['other_sta'].iloc[0,2]
    print(res.loc[col])