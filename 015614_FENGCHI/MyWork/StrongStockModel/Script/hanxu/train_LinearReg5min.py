# @Time : 2020/10/14 15:59
# @Author : Zhichen Lu
# @File : train_LinearReg5min.py


import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
import pandas as pd
from StrongStockModel.model.Modelmpl.LinearRegression import LinearRegression
from StrongStockModel.conf.path_config import strong_stock_path, root_path
from StrongStockModel.conf.model_param_config import best_param_linear
from xquant.compute.aimr import AIMR

param_list = [(0, (20150730, 20151225, 20151228, 20160111)),
              (1, (20150813, 20160111, 20160112, 20160125)),
              (2, (20150827, 20160125, 20160126, 20160215)),
              (3, (20150914, 20160215, 20160216, 20160229)),
              (4, (20150928, 20160229, 20160301, 20160314)),
              (5, (20151019, 20160314, 20160315, 20160328)),
              (6, (20151102, 20160328, 20160329, 20160412)),
              (7, (20151116, 20160412, 20160413, 20160426)),
              (8, (20151130, 20160426, 20160427, 20160511)),
              (9, (20151214, 20160511, 20160512, 20160525)),
              (10, (20151228, 20160525, 20160526, 20160608)),
              (11, (20160112, 20160608, 20160613, 20160624)),
              (12, (20160126, 20160624, 20160627, 20160708)),
              (13, (20160216, 20160708, 20160711, 20160722)),
              (14, (20160301, 20160722, 20160725, 20160805)),
              (15, (20160315, 20160805, 20160808, 20160819)),
              (16, (20160329, 20160819, 20160822, 20160902)),
              (17, (20160413, 20160902, 20160905, 20160920)),
              (18, (20160427, 20160920, 20160921, 20161011)),
              (19, (20160512, 20161011, 20161012, 20161025)),
              (20, (20160526, 20161025, 20161026, 20161108)),
              (21, (20160613, 20161108, 20161109, 20161122)),
              (22, (20160627, 20161122, 20161123, 20161206)),
              (23, (20160711, 20161206, 20161207, 20161220)),
              (24, (20160725, 20161220, 20161221, 20170104)),
              (25, (20160808, 20170104, 20170105, 20170118)),
              (26, (20160822, 20170118, 20170119, 20170208)),
              (27, (20160905, 20170208, 20170209, 20170222)),
              (28, (20160921, 20170222, 20170223, 20170308)),
              (29, (20161012, 20170308, 20170309, 20170322)),
              (30, (20161026, 20170322, 20170323, 20170407)),
              (31, (20161109, 20170407, 20170410, 20170421)),
              (32, (20161123, 20170421, 20170424, 20170508)),
              (33, (20161207, 20170508, 20170509, 20170522)),
              (34, (20161221, 20170522, 20170523, 20170607)),
              (35, (20170105, 20170607, 20170608, 20170621)),
              (36, (20170119, 20170621, 20170622, 20170705)),
              (37, (20170209, 20170705, 20170706, 20170719)),
              (38, (20170223, 20170719, 20170720, 20170802)),
              (39, (20170309, 20170802, 20170803, 20170816)),
              (40, (20170323, 20170816, 20170817, 20170830)),
              (41, (20170410, 20170830, 20170831, 20170913)),
              (42, (20170424, 20170913, 20170914, 20170927)),
              (43, (20170509, 20170927, 20170928, 20171018)),
              (44, (20170523, 20171018, 20171019, 20171101)),
              (45, (20170608, 20171101, 20171102, 20171115)),
              (46, (20170622, 20171115, 20171116, 20171129)),
              (47, (20170706, 20171129, 20171130, 20171213)),
              (48, (20170720, 20171213, 20171214, 20171227)),
              (49, (20170803, 20171227, 20171228, 20180111)),
              (50, (20170817, 20180111, 20180112, 20180125)),
              (51, (20170831, 20180125, 20180126, 20180208)),
              (52, (20170914, 20180208, 20180209, 20180301)),
              (53, (20170928, 20180301, 20180302, 20180315)),
              (54, (20171019, 20180315, 20180316, 20180329)),
              (55, (20171102, 20180329, 20180330, 20180416)),
              (56, (20171116, 20180416, 20180417, 20180502)),
              (57, (20171130, 20180502, 20180503, 20180516)),
              (58, (20171214, 20180516, 20180517, 20180530)),
              (59, (20171228, 20180530, 20180531, 20180613)),
              (60, (20180112, 20180613, 20180614, 20180628)),
              (61, (20180126, 20180628, 20180629, 20180712)),
              (62, (20180209, 20180712, 20180713, 20180726)),
              (63, (20180302, 20180726, 20180727, 20180809)),
              (64, (20180316, 20180809, 20180810, 20180823)),
              (65, (20180330, 20180823, 20180824, 20180906)),
              (66, (20180417, 20180906, 20180907, 20180920)),
              (67, (20180503, 20180920, 20180921, 20181012)),
              (68, (20180517, 20181012, 20181015, 20181026)),
              (69, (20180531, 20181026, 20181029, 20181109)),
              (70, (20180614, 20181109, 20181112, 20181123)),
              (71, (20180629, 20181123, 20181126, 20181207)),
              (72, (20180713, 20181207, 20181210, 20181221))]


def main_window_search(i):

    train_period = 20
    test_period = 2
    factor_num = 180
    N = 40
    all_mkt_preprocessed_ts_norm_by_date_path = '/data/group/800319/JunkSmallFactor/'  # root_path + 'processed_factor_all_pool_by_date_5min/ts_norm_%d_append/'%N
    #para = param_list[i][1]
    #print(para)
    base_dir = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/' \
               'Linear5min180_train%d_test%d_factor_num%d_norm_window_%d/' % (train_period, test_period, factor_num, N)
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    #if os.path.exists(base_dir + '%d.pkl' % para[1]):
     #   print(base_dir + '%d.pkl' % para[1], 'exist')
     #   return
    #print(base_dir + '%d.pkl' % para[1], 'start')
    #model = LinearRegression(para[0], para[-1], None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path)
    model = LinearRegression(20150730, 20181231, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path) #200

    best_param_linear['val_pred_path'] = base_dir + '_val_pred/'
    best_param_linear['train_pred_path'] = base_dir + '_train_pred/'
    best_param_linear['model_conf_path'] = base_dir + '_model_conf/'
    best_param_linear['load local model'] = True
    if not os.path.exists(best_param_linear['val_pred_path']):
        os.mkdir(best_param_linear['val_pred_path'])
    if not os.path.exists(best_param_linear['train_pred_path']):
        os.mkdir(best_param_linear['train_pred_path'])
    if not os.path.exists(best_param_linear['model_conf_path']):
        os.mkdir(best_param_linear['model_conf_path'])

    label = model.rolling_train_and_predict(params=best_param_linear, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=10, factor_nums=factor_num)

    #pd.to_pickle(label, base_dir + '%d.pkl' % para[1])
    # os.mkdir('/data/group/800319/Faamonitor/PL/')
    #print(base_dir + '%d.pkl' % para[1])


idx = 1  # int(AIMR.getParam())
main_window_search(idx)

from sklearn.linear_model import LinearRegression