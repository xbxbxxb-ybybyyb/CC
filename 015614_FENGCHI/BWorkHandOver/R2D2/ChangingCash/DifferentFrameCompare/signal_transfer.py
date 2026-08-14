# @Time : 2022/4/12 9:20
# @Author : Zhichen Lu
# @File : signal_transfer.py

import pandas as pd
import os

paper_signal_path = '/data/group/800442/800319/Timing/ReportFactor/Strategy/'   # 论文复现的策略
out_signal_path = '/data/group/800442/800319/Timing/BackTest/FormatedSignal/'   # 信号转换后的路径地址
paper_signal_list = list(filter(lambda x: 'fix' in x, os.listdir(paper_signal_path)))
for each in paper_signal_list:
    temp = pd.read_pickle(f'{paper_signal_path}{each}')
    temp.index = temp.index.astype(int)
    temp.columns = temp.columns.astype(int)
    temp = temp.stack() + 1
    pd.to_pickle(temp, f'{out_signal_path}{each}')
    print(each)

hx_signal_path = '/data/group/800442/800319/Timing/BackTest/Signal/'
# hx_signal_path = '/data/group/800442/800319/Timing/BackTest/SignalReduce/'

# hx_signal_list = ['XGB300Reduce','long_pred_XGB300Reduce','short_pred_XGB300Reduce']
hx_signal_list = ['long_pred_XGB300', 'short_pred_XGB300']
# hx_signal_list = ['DiscreteXGB300', 'DcXGB300']
# hx_signal_list = ['DiscreteXGB600300gain_mdd_pos_stack', 'DiscreteXGB600300']
for each in hx_signal_list:
    hx_signal = pd.read_pickle(f'{hx_signal_path}/{each}.pkl')
    hx_signal = hx_signal['yh'].stack() + 1
    pd.to_pickle(hx_signal, f'{out_signal_path}/{each}.pkl')

wyl_signal_path = '/data/group/800442/800319/Timing/FixFactor/FixFactor/wyl/signal/'
signal_list = ['ff_grasp_discrete_600_50_0.25_0.01_25.pkl']#sorted(os.listdir(wyl_signal_path))
wyl = []
for each in signal_list:
    if not each.endswith('.pkl'):
        continue
    wyl.append(each.replace('.pkl', ''))
    if os.path.exists(f'{out_signal_path}/{each}'):
        print(each, 'exist')
        continue
    temp = pd.read_pickle(f'/data/group/800442/800319/Timing/FixFactor/FixFactor/wyl/signal/{each}')
    # temp = temp['yh'].stack() + 1
    tag = temp.columns.levels[0].tolist()
    if len(tag) != 1:
        raise Exception('Non Indentical tag')
    tag = tag[0]
    temp = temp[tag].stack() + 1
    pd.to_pickle(temp, f'{out_signal_path}/{each}')

wyl = ['pct10_longins_700_10', 'pct10_shortins_longshortins_350_10', 'pct15_longins_700_10', 'pct15_longshortins_550_10', 'pct15_shortins_350_10', 'pct20_longins_950_10',
       'pct20_longshortins_700_12', 'pct20_shortins_350_12', 'pct25_longins_700_10', 'pct25_longshortins_550_10', 'pct25_shortins_350_10', 'pct30_longins_longshortins_700_8',
       'pct30_shortins_450_8', 'pct32_shortins_1150_4', 'pct32_shortins_250_6', 'pct32_shortins_700_6', 'pct35_shortins_1150_2', 'pct35_shortins_150_4', 'pct35_shortins_550_6',
       'pct40_shortins_1150_0', 'pct40_shortins_150_2', 'pct40_shortins_500_4', 'pct45_shortins_200_0', 'pct45_shortins_700_0', 'pct45_shortins_750_0']

# xq_signal_list = ['/data/group/800442/800319/Timing/ReportFactor/Strategy/SMT_GF_abs_dis_signal_5d.pkl',
#                   '/data/group/800442/800319/Timing/Model/SVR/Signal/Long300_Short200_SVR.pkl',
#                   '/data/group/800442/800319/Timing/Model/SVR/Signal/Long100_Short200_SVR.pkl']
xq_signal_list = ['/data/group/800442/800319/Timing/Model/LSTM/Signal/LSTM_Dc300_reduce_T60_wf1d1000_pct_60d_60_0.3.pkl',
                  '/data/group/800442/800319/Timing/Model/LSTM/Signal/LSTM300_reduce_T60wf1d1000_pct_60d_60_0.3.pkl']

['/data/group/800442/800319/Timing/Model/SVRRollingMonth/Signal/DcFactorNum300_reduce_40_0.3.pkl',
                  '/data/group/800442/800319/Timing/Model/SVRRollingMonth/Signal/DcFactorNum300_reduce_60_0.3.pkl',
                  '/data/group/800442/800319/Timing/Model/SVRRollingMonth/Signal/DcFactorNum300_reduce_long_short_pred.pkl',
                  '/data/group/800442/800319/Timing/Model/LightGBM/Signal/LGBM_Dc300_reduce_NoScalar_long_short_pred.pkl',
                  '/data/group/800442/800319/Timing/Model/LightGBM/Signal/LGBM_Dc300_reduce_NoScalar_60_0.3.pkl']
['/data/group/800442/800319/Timing/Model/SVRRollingMonth/Signal/DcFactorNum300_ff_40_0.3.pkl',
 '/data/group/800442/800319/Timing/Model/SVRRollingMonth/Signal/DcFactorNum300_ff_60_0.3.pkl',
 '/data/group/800442/800319/Timing/Model/SVRRollingMonth/Signal/DcFactorNum300_ff_long_short_pred.pkl']

['/data/group/800442/800319/Timing/Model/SVRRollingMonth/Signal/DcFactorNum300_SVR.pkl',
 '/data/group/800442/800319/Timing/ReportFactor/Strategy/EMDT_trend_fix_signal_20220429.pkl']
['/data/group/800442/800319/Timing/Model/SVRRollingMonth/Signal/FactorNum300_SVR_V1_20220426.pkl',
 '/data/group/800442/800319/Timing/Model/SVRRollingMonth/Signal/FactorNum300_SVR_V2_20220426.pkl',
 '/data/group/800442/800319/Timing/Model/SVRRollingMonth/Signal/FactorNum300_SVR_V3_20220426.pkl']

['/data/group/800442/800319/Timing/ReportFactor/Strategy/EMDT_trend_signal_20220421.pkl',
 '/data/group/800442/800319/Timing/ReportFactor/Strategy/EMDT_trend_fix_signal_20220421.pkl',
 '/data/group/800442/800319/Timing/Model/SVR/Signal/Long100_Short200_SVR_20220421.pkl']

name_list = []
for each in xq_signal_list:
    temp = pd.read_pickle(each)
    if isinstance(temp.columns.tolist()[0], tuple):
        temp = temp['yh']
    temp.index = temp.index.astype(int)
    temp.columns = temp.columns.astype(int)
    temp = temp.stack() + 1
    name = os.path.split(each)[-1]
    pd.to_pickle(temp, f'{out_signal_path}/{name}')
    name_list.append(name.replace('.pkl', ''))

xq = ['SMT_GF_abs_dis_signal_5d', 'Long300_Short200_SVR', 'Long100_Short200_SVR']
['pct10_longins_700_10', 'pct10_shortins_longshortins_350_10', 'pct15_longins_700_10', 'pct15_longshortins_550_10', 'pct15_shortins_350_10', 'pct20_longins_950_10',
 'pct20_longshortins_700_12', 'pct20_shortins_350_12', 'pct25_longins_700_10', 'pct25_longshortins_550_10', 'pct25_shortins_350_10', 'pct30_longins_longshortins_700_8',
 'pct30_shortins_450_8', 'pct32_shortins_1150_4', 'pct32_shortins_250_6', 'pct32_shortins_700_6', 'pct35_shortins_1150_2', 'pct35_shortins_150_4', 'pct35_shortins_550_6',
 'pct40_shortins_1150_0', 'pct40_shortins_150_2', 'pct40_shortins_500_4', 'pct45_shortins_200_0', 'pct45_shortins_700_0', 'pct45_shortins_750_0', 'SMT_GF_abs_dis_signal_5d',
 'Long300_Short200_SVR', 'Long100_Short200_SVR', 'DiscreteXGB300', 'DcXGB300', 'NoTiming']
