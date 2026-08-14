# @Time : 2020/9/28 11:13
# @Author : Zhichen Lu
# @File : train_lr.py

import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
import pandas as pd
from StrongStockModel.model.Modelmpl.Linear_out_sample import LinearReg
from xquant.compute.aimr import AIMR

para_list = [(0, (20180309, 20181228, 20190102, 20190115)),
 (1, (20180323, 20190115, 20190116, 20190129)),
 (2, (20180410, 20190129, 20190130, 20190219)),
 (3, (20180424, 20190219, 20190220, 20190305)),
 (4, (20180510, 20190305, 20190306, 20190319)),
 (5, (20180524, 20190319, 20190320, 20190402)),
 (6, (20180607, 20190402, 20190403, 20190417)),
 (7, (20180622, 20190417, 20190418, 20190506)),
 (8, (20180706, 20190506, 20190507, 20190520)),
 (9, (20180720, 20190520, 20190521, 20190603)),
 (10, (20180803, 20190603, 20190604, 20190618)),
 (11, (20180817, 20190618, 20190619, 20190702)),
 (12, (20180831, 20190702, 20190703, 20190716)),
 (13, (20180914, 20190716, 20190717, 20190730)),
 (14, (20181008, 20190730, 20190731, 20190813)),
 (15, (20181022, 20190813, 20190814, 20190827)),
 (16, (20181105, 20190827, 20190828, 20190910)),
 (17, (20181119, 20190910, 20190911, 20190925)),
 (18, (20181203, 20190925, 20190926, 20191016)),
 (19, (20181217, 20191016, 20191017, 20191030)),
 (20, (20190102, 20191030, 20191031, 20191113)),
 (21, (20190116, 20191113, 20191114, 20191127)),
 (22, (20190130, 20191127, 20191128, 20191211)),
 (23, (20190220, 20191211, 20191212, 20191225)),
 (24, (20190306, 20191225, 20191226, 20200109)),
 (25, (20190320, 20200109, 20200110, 20200123)),
 (26, (20190403, 20200123, 20200203, 20200214)),
 (27, (20190418, 20200214, 20200217, 20200228)),
 (28, (20190507, 20200228, 20200302, 20200313)),
 (29, (20190521, 20200313, 20200316, 20200327)),
 (30, (20190604, 20200327, 20200330, 20200413)),
 (31, (20190619, 20200413, 20200414, 20200427)),
 (32, (20190703, 20200427, 20200428, 20200514)),
 (33, (20190717, 20200514, 20200515, 20200528)),
 (34, (20190731, 20200528, 20200529, 20200611)),
 (35, (20190814, 20200611, 20200612, 20200629)),
 (36, (20190828, 20200629, 20200630, 20200713)),
 (37, (20190911, 20200713, 20200714, 20200727)),
 (38, (20190926, 20200727, 20200728, 20200810)),
 (39, (20191017, 20200810, 20200811, 20200824)),
 (40, (20191031, 20200824, 20200825, 20200907)),
 (41, (20191114, 20200907, 20200908, 20200921)),
 (42, (20191128, 20200921, 20200922, 20201013)),
 (43, (20191212, 20201013, 20201014, 20201027))]


def main(i):
    train_period = 1
    test_period = 10
    factor_num = 400
    N = 40
    all_mkt_preprocessed_ts_norm_by_date_path = '/data/group/800319/junkData/StrongStock/processed_factor_all_pool_by_date/ts_norm_%d/' % N
    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/out_of_sample/lr/lr_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
        train_period, test_period, factor_num, N)

    best_param = {'n_jobs':-1}
    train_start, train_end, test_start, test_end = para_list[i][1]
    print(train_start, train_end, test_start, test_end)

    best_param['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param['train_log_path'] = out_file.replace('.pkl', '_train_log/')
    best_param['model_conf_path'] = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/out_of_sample/lr/lr_train199_test1_factor_num400_norm_window_40_model_conf/'
    best_param['load local model'] = True
    if not os.path.exists(best_param['model_conf_path']):
        os.mkdir(best_param['model_conf_path'])
    # best_param['load local model'] = True
    # if os.path.exists(best_param['model_conf_path'] + '%d.pkl' % train_end):
    #     print(best_param['model_conf_path'] + '%d.pkl' % train_end, 'exist')
    #     return
    model = LinearReg(train_end,test_end, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path)
    label = model.rolling_train_and_predict(params=best_param, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=10, factor_nums=factor_num)
    pd.to_pickle(label, out_file.replace('.pkl', '_%d.pkl' % train_end))
    # pd.to_pickle(label, out_file)
    # os.mkdir('/data/group/800319/Faamonitor/PL/')

idx = AIMR.getParam()
main(idx)