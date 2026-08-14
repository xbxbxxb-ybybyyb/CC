# @Time : 2021/8/19 13:43
# @Author : Zhichen Lu
# @File : data_validation.py

from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
import configparser
import pandas as pd
from dataApi.getData import get_minute_1factor
conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

train_start,train_end,test_start,test_end = para_list[-1][1]

ml = ModelNewLoading(train_start, test_end, None, feature_address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust_old/data/',
                                          factor_eval_indicator='ic_d',
                                          factor_num=400)
fix_factor_list = pd.read_pickle('/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400_factor_list/20210813.pkl')
train_feature, train_label, test_feature, test_label,_ = ml.get_dataset((train_start,train_end),(test_start,test_end),fix_factor_list,None,None)

minute = get_minute_1factor('close_badj',start_datetime=train_start,end_datetime=test_end)
close_badj = minute.swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]].swaplevel(0,1)
ret = close_badj.pct_change(7).shift(-7)
train_label['close_label'] = ret.loc[:train_end].stack(dropna=False)
test_label['close_label'] = ret.loc[test_start:].stack(dropna=False)


# check = train_label.groupby(level=0).apply(lambda x : x)

corr_train = train_label.groupby(level=0).apply(lambda x : x.corr().values[0,1])

train_label.loc[20210813].corr()
test_label.loc[20210817].corr()


