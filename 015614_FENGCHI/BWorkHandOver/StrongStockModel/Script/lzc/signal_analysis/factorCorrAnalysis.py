# @Time : 2021/3/25 0:01
# @Author : Zhichen Lu
# @File : factorCorrAnalysis.py
import pandas as pd
import os
import configparser
from tqdm import tqdm
conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

signal_dict={
# 'Cat':'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
#  'LightGBM':'/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
'XGB_C':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'XGB_D':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'XGB_T':'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
}

corr = {}
corr_daily = []
val_corr = {}
for i in tqdm(range(73)):
    train_end = para_list[i][1][1]
    temp_dict = {}
    temp_corr = {}
    temp_corr_daily = {}
    temp_val_corr = {}
    for each in signal_dict:
        temp_dict[each] = pd.read_pickle(signal_dict[each].replace('.pkl','/%d.pkl'%train_end))
        temp_corr[each] = temp_dict[each].corr().values[0,1]
        temp_corr_daily[each] = temp_dict[each].groupby(level=0).apply(lambda x : x.corr().values[0,1])
    temp_dict = pd.Panel(temp_dict)
    integrate = temp_dict.sum(axis='items')/temp_dict.count(axis='items')
    temp_corr['集成'] = integrate.corr().values[0,1]
    temp_corr_daily['集成'] = integrate.groupby(level=0).apply(lambda x : x.corr().values[0,1])
    temp_corr_daily = pd.DataFrame(temp_corr_daily)
    corr_daily.append(temp_corr_daily)
    corr['%d-%d'%para_list[i][1][2:]] = temp_corr
    print(train_end)

corr = pd.DataFrame(corr).T
corr_daily = pd.concat(corr_daily)
with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/数据分析/样本内IC_XGB.xlsx') as writer:
    corr.to_excel(writer,sheet_name='每期IC')
    corr_daily.to_excel(writer,sheet_name='每日IC')
writer.close()


import pandas as pd

data = pd.read_excel('/data/user/015664/AFuckingTrigger/数据分析/样本内IC.xlsx',sheet_name=None)
daily_IC = data['每日IC'].set_index('date')
mdd_list = []
temp_prof_comp = daily_IC['万德全A']
cummax = temp_prof_comp.cummax()
cum_mdd = ( (cummax- temp_prof_comp)/temp_prof_comp)#.drop('year',axis=1)

cum_mdd.to_excel('/data/user/015664/AFuckingTrigger/数据分析/CUMMDD.xlsx')

start = cum_mdd.index[0]
end = cum_mdd.index[0]
pred_end = cum_mdd.index[0]
max_val = 0
for date in cum_mdd.index:
    if cum_mdd.loc[date]>max_val:
        max_val =
