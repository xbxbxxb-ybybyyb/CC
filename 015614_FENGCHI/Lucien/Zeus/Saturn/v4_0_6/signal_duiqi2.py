# coding: utf-8
# Author：fengchi863
# Date ：2023/5/16 10:21

"""
对齐Europa样本，即如果Europa前一天买了，那么第二天Saturn就不买了，进行如下测试
"""

import pandas as pd
from dataApi.tradeDate import get_pre_trade_date

europa_period1_signal_fpath = '/data/group/800463/wangj/save_files/Europa_v3/Europa_realout_testfit_v3_fac_20230317_maxbeta_final_noroll_merge6models_20230328.csv'
europa_period1_signal = pd.read_csv(open(europa_period1_signal_fpath)).set_index(['Indexs'])
europa_period1_signal = europa_period1_signal.query('vote_sum_pred >= 3')

europa_period1_signal['next_datelist'] = europa_period1_signal['datelist'].apply(lambda x: get_pre_trade_date(x, -1))
europa_period1_signal['Indexs'] = europa_period1_signal.apply(lambda x: x['stockID'] + ' ' + str(x['next_datelist']), axis=1)
europa_period1_signal = europa_period1_signal.set_index('Indexs').sort_values('next_datelist')
europa_period1_signal['buy_singal'] = 1

# 开始读取对齐
from Zeus.Saturn.v4_0_6.path_conf import date_config
PERIOD = 'period3'
SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
date_dict = date_config[f'{PERIOD}']
pred_type = 'fit'
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']

pred_data_fpath_list = [
    # f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv8_XgbRegModel/{out_begin}~{out_end}_fsv8_XgbRegModel_{SUB_VERSION}.csv',
    # f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv10_XgbRegModel/{out_begin}~{out_end}_fsv10_XgbRegModel_{SUB_VERSION}.csv',
    # f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv11_XgbRegModel/{out_begin}~{out_end}_fsv11_XgbRegModel_{SUB_VERSION}.csv',
    # f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/rffs_XgbRegModel/{out_begin}~{out_end}_rffs_XgbRegModel_{SUB_VERSION}.csv',
    #
    # f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv8_AllXgbRegModel/{out_begin}~{out_end}_fsv8_AllXgbRegModel_{SUB_VERSION}.csv',
    # f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv10_AllXgbRegModel/{out_begin}~{out_end}_fsv10_AllXgbRegModel_{SUB_VERSION}.csv',
    # f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv11_AllXgbRegModel/{out_begin}~{out_end}_fsv11_AllXgbRegModel_{SUB_VERSION}.csv',
    # f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/rffs_AllXgbRegModel/{out_begin}~{out_end}_rffs_AllXgbRegModel_{SUB_VERSION}.csv',

    f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/duiqi_{out_begin}~{out_end}_fsv8_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/duiqi_{out_begin}~{out_end}_fsv10_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/duiqi_{out_begin}~{out_end}_fsv11_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/duiqi_{out_begin}~{out_end}_rffs_AllXgbRegModel_{SUB_VERSION}.csv',
]


for pred_data_fpath in pred_data_fpath_list:
    print(pred_data_fpath)
    filtered_samples_index = pd.read_csv(pred_data_fpath, index_col=0).index
    filtered_samples = pd.read_csv(pred_data_fpath, index_col=0)
    model_name = pred_data_fpath.split('_')[-3] + '_' + pred_data_fpath.split('_')[-2]

    ret = pd.concat([filtered_samples, europa_period1_signal['buy_singal']], axis=1).query('buy_singal != 1').sort_values(['datelist'])
    ret.index.names = ['Indexs']
    # ret.to_csv('/data/user/015614/Zeus/pred/Saturn/v4_0_6/' + f'dropEuropa_{out_begin}~{out_end}_{model_name}_{SUB_VERSION}.csv')
    ret.to_csv('/data/user/015614/Zeus/pred/Saturn/v4_0_6/' + f'dropEuropa_duiqi_{out_begin}~{out_end}_{model_name}_{SUB_VERSION}.csv')
