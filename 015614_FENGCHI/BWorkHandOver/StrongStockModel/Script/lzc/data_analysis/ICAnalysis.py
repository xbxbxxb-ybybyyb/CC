# @Time : 2020/12/7 9:01
# @Author : Zhichen Lu
# @File : ICAnalysis.py

import pandas as pd
import os

base_path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/'
param_list = [(0, (20150309, 20151225, 20151228, 20160111)),
              (1, (20150323, 20160111, 20160112, 20160125)),
              (2, (20150407, 20160125, 20160126, 20160215)),
              (3, (20150421, 20160215, 20160216, 20160229)),
              (4, (20150506, 20160229, 20160301, 20160314)),
              (5, (20150520, 20160314, 20160315, 20160328)),
              (6, (20150603, 20160328, 20160329, 20160412)),
              (7, (20150617, 20160412, 20160413, 20160426)),
              (8, (20150702, 20160426, 20160427, 20160511)),
              (9, (20150716, 20160511, 20160512, 20160525)),
              (10, (20150730, 20160525, 20160526, 20160608)),
              (11, (20150813, 20160608, 20160613, 20160624)),
              (12, (20150827, 20160624, 20160627, 20160708)),
              (13, (20150914, 20160708, 20160711, 20160722)),
              (14, (20150928, 20160722, 20160725, 20160805)),
              (15, (20151019, 20160805, 20160808, 20160819)),
              (16, (20151102, 20160819, 20160822, 20160902)),
              (17, (20151116, 20160902, 20160905, 20160920)),
              (18, (20151130, 20160920, 20160921, 20161011)),
              (19, (20151214, 20161011, 20161012, 20161025)),
              (20, (20151228, 20161025, 20161026, 20161108)),
              (21, (20160112, 20161108, 20161109, 20161122)),
              (22, (20160126, 20161122, 20161123, 20161206)),
              (23, (20160216, 20161206, 20161207, 20161220)),
              (24, (20160301, 20161220, 20161221, 20170104)),
              (25, (20160315, 20170104, 20170105, 20170118)),
              (26, (20160329, 20170118, 20170119, 20170208)),
              (27, (20160413, 20170208, 20170209, 20170222)),
              (28, (20160427, 20170222, 20170223, 20170308)),
              (29, (20160512, 20170308, 20170309, 20170322)),
              (30, (20160526, 20170322, 20170323, 20170407)),
              (31, (20160613, 20170407, 20170410, 20170421)),
              (32, (20160627, 20170421, 20170424, 20170508)),
              (33, (20160711, 20170508, 20170509, 20170522)),
              (34, (20160725, 20170522, 20170523, 20170607)),
              (35, (20160808, 20170607, 20170608, 20170621)),
              (36, (20160822, 20170621, 20170622, 20170705)),
              (37, (20160905, 20170705, 20170706, 20170719)),
              (38, (20160921, 20170719, 20170720, 20170802)),
              (39, (20161012, 20170802, 20170803, 20170816)),
              (40, (20161026, 20170816, 20170817, 20170830)),
              (41, (20161109, 20170830, 20170831, 20170913)),
              (42, (20161123, 20170913, 20170914, 20170927)),
              (43, (20161207, 20170927, 20170928, 20171018)),
              (44, (20161221, 20171018, 20171019, 20171101)),
              (45, (20170105, 20171101, 20171102, 20171115)),
              (46, (20170119, 20171115, 20171116, 20171129)),
              (47, (20170209, 20171129, 20171130, 20171213)),
              (48, (20170223, 20171213, 20171214, 20171227)),
              (49, (20170309, 20171227, 20171228, 20180111)),
              (50, (20170323, 20180111, 20180112, 20180125)),
              (51, (20170410, 20180125, 20180126, 20180208)),
              (52, (20170424, 20180208, 20180209, 20180301)),
              (53, (20170509, 20180301, 20180302, 20180315)),
              (54, (20170523, 20180315, 20180316, 20180329)),
              (55, (20170608, 20180329, 20180330, 20180416)),
              (56, (20170622, 20180416, 20180417, 20180502)),
              (57, (20170706, 20180502, 20180503, 20180516)),
              (58, (20170720, 20180516, 20180517, 20180530)),
              (59, (20170803, 20180530, 20180531, 20180613)),
              (60, (20170817, 20180613, 20180614, 20180628)),
              (61, (20170831, 20180628, 20180629, 20180712)),
              (62, (20170914, 20180712, 20180713, 20180726)),
              (63, (20170928, 20180726, 20180727, 20180809)),
              (64, (20171019, 20180809, 20180810, 20180823)),
              (65, (20171102, 20180823, 20180824, 20180906)),
              (66, (20171116, 20180906, 20180907, 20180920)),
              (67, (20171130, 20180920, 20180921, 20181012)),
              (68, (20171214, 20181012, 20181015, 20181026)),
              (69, (20171228, 20181026, 20181029, 20181109)),
              (70, (20180112, 20181109, 20181112, 20181123)),
              (71, (20180126, 20181123, 20181126, 20181207)),
              (72, (20180209, 20181207, 20181210, 20181221))]


file_list = os.listdir(base_path)
file_list = list(filter(lambda x : '.pkl' in x and '100' not in x,file_list))
file_list = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_std_adjusted_train200_test10_factor_num400_norm_window_40.pkl']
IC_compare = {}
label = {}

for each in file_list:
    name = each.replace('_train200_test10_factor_num400_norm_window_40.pkl','')
    label[name] = pd.read_pickle(each)
    IC_compare[name] = label[name].corr().values[0,1]
IC_compare = pd.Series(IC_compare)

IC_modelly_val = {}
IC_modelly_test ={}

for each in file_list:
    name = each.replace('_train200_test10_factor_num400_norm_window_40.pkl', '')
    modelly_val_ic_list = {}
    modelly_test_ic_list = {}
    for idx,cell in param_list:
        train_start,train_end,test_start,test_end = cell
        val_label = pd.read_pickle(each.replace('.pkl','_val_pred/')+'%d.pkl'%train_end)
        modelly_val_ic_list[train_end] = val_label.corr().values[0,1]
        modelly_test_ic_list[train_end] = label[name].loc[test_start:test_end].corr().values[0,1]
    IC_modelly_val[name] = pd.Series(modelly_val_ic_list)
    IC_modelly_test[name] = pd.Series(modelly_test_ic_list)

compare = pd.DataFrame({'all_ic':IC_compare,
                        'modelly_test_set_ic':pd.Series({x:IC_modelly_test[x].mean() for x in IC_modelly_test}),
                        'modelly_val_set_ic':pd.Series({x:IC_modelly_val[x].mean() for x in IC_modelly_val})})

compare = compare.sort_values('modelly_test_set_ic',ascending=False)



import pandas as pd
import os
import numpy as np
from dataApi.getData import get_minute_1factor
signal,pred_ret = pd.read_pickle('/data/group/800319/信号存储/signal_XGB_DTC20201214.pkl')
pred_ret = pred_ret.replace(0,np.nan)
close_adj = get_minute_1factor('close_badj',start_datetime=20151220,end_datetime=20181231,code_list=pred_ret.columns.tolist())
close_adj_fix = close_adj.swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]].swaplevel(0,1)
ret = close_adj_fix.shift(-7)/close_adj_fix - 1
ret = ret.loc[pred_ret.index]

pred_ret_stack = pred_ret.stack(dropna=False).to_frame()
ret_stack = ret.stack(dropna=False).to_frame()

compare = pd.concat([pred_ret_stack,ret_stack],axis=1)
compare.columns = ['pred_ret','ret']
compare = compare.dropna()
compare.corr()

signal_stack = signal.stack().to_frame().loc[compare.index]

check = compare[signal_stack[0]]
check.mean()

check1 = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl')
check2 = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl')

signal = pd.Panel({'d':check1,'t':check2})
signal_count = signal.count(axis=0)
signal_sum = signal.sum(axis=0)
signal = signal_sum / signal_count
signal[signal_count.eq(0)] = np.nan
signal.corr()