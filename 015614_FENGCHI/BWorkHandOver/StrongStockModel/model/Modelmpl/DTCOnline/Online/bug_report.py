# @Time : 2021/7/20 10:15
# @Author : Zhichen Lu
# @File : bug_report.py

from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering
from dataApi.tradeDate import get_date_range,get_pre_trade_date,get_recent_trade_date
from dataApi.LoadingTool import trans_df2arr
from StrongStockModel.conf.path_config import root_path
import pandas as pd
import numpy as np

label = pd.read_pickle(f'{root_path}labels/future_480.pkl')
fix_factor_list = ['AbnormalPriceDiff', 'AbnormalReturnPVCorrBias20d', 'AbnormalVolumePVCorr']

train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time = load_fix_data(20160301, 20161220, fix_factor_list)
check_train_label = trans_df2arr(label.loc[20160301: 20161220], start_date=20160301, end_date=20161220)

nan_tag = np.isnan(check_train_label) & (~np.isnan(train_label))
nana_index = list(zip(train_idx_date[nan_tag].tolist(),train_idx_time[nan_tag].tolist(),train_idx_code[nan_tag].tolist()))
nana_index[0]
train_idx_date[52],train_idx_time[52],train_idx_code[52]
check_train_label[52]
label.loc[20160301,157] # not nan

