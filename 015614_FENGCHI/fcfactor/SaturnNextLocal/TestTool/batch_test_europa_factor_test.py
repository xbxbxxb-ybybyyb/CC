# coding: utf-8
# Author：fengchi863
# Date ：2023/8/31 9:43

import sys
import os
sys.path.append('/data/user/015614/fcfactor')

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
import IO as IO
import importlib
import datetime as dt
import gc
import time
from datetime import datetime, timedelta
from joblib import Parallel, delayed
from SaturnNextLocal.TestTool.run_factor_demo import run_factor
from SaturnNextLocal.TestTool.project_2_factor_test_origin import pj2FactorTest
from scipy import stats

# def judge_factor_type(factor_name):
#     factor_name_list = factor_name.split('_')
#     factor_type = factor_name_list[1] + '_' + factor_name_list[2]
#     if factor_name_list[2].startswith('202'):
#         factor_type = factor_name_list[1]
#     if factor_type == 'T1':
#         return 'Next_T-1_factor'
#     elif factor_type == 'trans':
#         return 'Next1mTransaction'
#     elif factor_type == 'ttickab':
#         return 'Next1mTickab'
#     elif factor_type == 'trans_order':
#         return None
#     elif factor_type == 'order':
#         return None
#     elif factor_type == 'trans_tickab':
#         return None

def judge_factor_type(factor_name):
    factor_name_list = factor_name.split('_')
    factor_type = factor_name_list[1] + '_' + factor_name_list[2]
    if factor_name_list[2].startswith('202'):
        factor_type = factor_name_list[1]
    if factor_type == 'T1':
        return None
    elif factor_type == 'trans':
        return 'TallTrans'
    elif factor_type == 'ttickab':
        return 'TallTick'
    elif factor_type == 'trans_order':
        return None
    elif factor_type == 'order':
        return None
    elif factor_type == 'trans_tickab':
        return None


def start_backtest(factor_df, result_path):
    bt_columns = ['nan_num', 'same_rate', 'value_diff_score', 'value_stability_score', 'mixed_diff_score',
                  'mixed_stability_score', 'score', 'corr_tot', 'high_corr_factor', 'high_corr_factor_corr', 'high_corr_s_num']
    res_df = pd.DataFrame(columns=bt_columns)

    # filter_factor = pd.read_pickle('/data/group/800463/data/project1_public/factor_lib_v2/filter_quickrise.pkl')
    # sft = strongFactorTest(self.start_date, self.end_date, filter_factor=filter_factor, filter_name='quickrise')
    sft = pj2FactorTest(start_date, end_date)  # 全样本下测试
    res_dict = sft.factor_test(factor_df, result_path='/data/user/015614/junkData/', factor_corr_test=True, generate_pdf=False)

    nan_num = res_dict['factor_information'].loc['Nan|Inf Count', 'Factor Info']
    same_rate = res_dict['max_same_ratio'].loc['repeated_ratio', 'first']
    value_diff_score = res_dict['check_score_res'].loc['score', 'value_diff_score']
    value_stability_score = res_dict['check_score_res'].loc['score', 'value_stability_score']
    mixed_diff_score = res_dict['check_score_res'].loc['score', 'class_diff_score']
    mixed_stability_score = res_dict['check_score_res'].loc['score', 'class_stability_score']
    score = res_dict['check_score_res'].loc['score', 'tot_score']
    corr_tot = res_dict['corr_sta'].loc['corr_tot', 'value']

    high_corr_s = res_dict['factor_corr'].query('factor_corr >= 0.7')
    if len(high_corr_s) == 0:
        high_corr_s = res_dict['factor_corr'].iloc[:2]
    else:
        high_corr_s = res_dict['factor_corr'].iloc[:len(high_corr_s) + 2]

    high_corr_factor_list_str = '，'.join(high_corr_s.index.tolist())
    high_corr_factor_corr_list_str = '，'.join(high_corr_s['factor_corr'].map(lambda x: round(x, 4)).map(str).tolist())

    factor_mean = factor_df.mean().values[0]
    factor_std = factor_df.std().values[0]
    if  factor_mean < 0.001 and factor_std < 0.001:
        print('!!!!!!!!!!!!!!!!因子波动小!!!!!!!!!!!!!!!!')
    print('=====>>>>', score, corr_tot, factor_mean, factor_std, high_corr_factor_list_str, high_corr_factor_corr_list_str)

if __name__ == '__main__':
    print('------------------开始跑因子-------------------')
    print('当前时间', dt.datetime.now().strftime('%H%M%S'))
    t1 = time.time()
    start_date, end_date = 20160101, 20191231
    basic_file_path = '/data/group/800463/data/project2_public/next_factor_lib/Basic_next_hf_finish_20160101_20191231.h5'
    result_path = f'/data/user/015614/factor/factor_digging_europa2saturnNext/'
    os.makedirs(result_path, exist_ok=True)
    factor_df = pd.DataFrame()
    sft = pj2FactorTest(start_date, end_date)

    # factor_type = 'T-1_factor'
    # factor_type = 'TTransaction_TOrder'
    # multi = False

    factor_fpath_list = list()
    factor_fname_list = list()
    for dat in [20230824, 20230831, 20230907, 20230914, 20230921, 20230928, 20231012, 20231019, 20231026, 20231102, 20231109, 20231116, 20231123, 20231130]:
        factor_fname = os.listdir(f'/data/user/015614/fcfactor/SaturnNextLocal/europa_factor_transfer/d{dat}/')
        factor_fname = list(filter(lambda x: not x.endswith('.xlsx') and x.startswith('factor_'), factor_fname))
        factor_fpath_list += list(map(lambda x: f'/data/user/015614/fcfactor/SaturnNextLocal/europa_factor_transfer/d{dat}/' + x, factor_fname))
        factor_fname_list += factor_fname

    this_submit_factor_dict = dict()
    for idx, factor_fname in enumerate(factor_fname_list):
        print(f'当前测试因子：{factor_fname}')
        factor_fpath = factor_fpath_list[idx]
        factor_fname = factor_fname[:-3]
        if factor_fname in list(map(lambda x: 'factor_' + x[:-3], os.listdir('/data/user/015614/factor/factor_digging_europa2saturnNext/'))):
            continue
        date = int(factor_fname.split('_')[-2])
        if len(str(date)) == 8:
            pass
        else:
            date = int(factor_fname.split('_')[-3])
        mod_name = f'SaturnNextLocal.europa_factor_transfer.d{date}.{factor_fname}'
        module = importlib.import_module(mod_name)
        func = getattr(module, factor_fname)
        factor_name = factor_fname[7:]
        factor_type = judge_factor_type(factor_name)
        if not factor_type:
            continue
        multi = True if factor_type != 'Next_T-1_factor' else False
        factor_df = run_factor(func, factor_name, factor_type, start_date, end_date, basic_file_path, result_path, param_tuple=(), interval_res=False, multi=multi)
        factor_df = factor_df.reindex(index=sft.basic_df.index)

        # check = IO.read_data([20160101, 20181231], alt='/data/user/018107/share_file/for_fc/fc_stk_zz1000_r_5.h5')
        # print(factor_df.describe())
        # print('结束时间', dt.datetime.now().strftime('%H%M%S'))
        # print('计算耗时', time.time() - t1)
        start_backtest(factor_df, result_path=result_path)

        # 计算和本次的相关性
        for this_submit_factor in this_submit_factor_dict.keys():
            this_submit_factor_df = this_submit_factor_dict[this_submit_factor]
            corr = stats.spearmanr(this_submit_factor_df[this_submit_factor].fillna(0), factor_df[factor_name].fillna(0))[0]
            if corr > 0.69: print('!!!!', this_submit_factor, corr)
        this_submit_factor_dict[factor_name] = factor_df






