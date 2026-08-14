# @Time : 2022/2/9 10:31
# @Author : Zhichen Lu
# @File : label_distribution.py
import pandas as pd
import os
res_path = '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV3With1DayLabel_20220126/Future_3_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/'
os.listdir(res_path)
check = pd.read_pickle(f'{res_path}/20190625.pkl')