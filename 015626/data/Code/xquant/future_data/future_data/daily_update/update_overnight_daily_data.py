from multifactor.IO import IO
import pandas as pd
import os
import datetime
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool

from multifactor.data.utils import *
import multifactor.utility.dt as udt
import time

import warnings
warnings.filterwarnings('ignore')

import pickle

def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
    
def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict    
        
class MinuteDataToDaily:
    """
    把分钟数据根据需要降频到日级别
    """

    def __init__(self, minute_data):
        self.minute_data = minute_data

    def get_trading_days(self):
        """
        获取原始分钟数据包含的所有交易日
        :return: np.ndarray
            原始分钟数据包含的所有交易日
        """
        trading_days = np.unique(self.minute_data.index.date)
        return trading_days

    def get_daily_minute_num(self):
        """
        获取原始分钟数据中的每个交易日有分钟bar
        :return: int
            每个交易日的分钟bar数量
        """
        daily_minute_num = int(self.minute_data.shape[0] / self.get_trading_days().shape[0])
        return daily_minute_num

    def truncated_time_index_num(self, truncated_time):
        """
        由于交易需要等原因，有时候每天的尾盘数据在开发因子时无法使用，需要把这部分数据截去
        这个函数用于确定要截断的时间位于当天的第几分钟
        :param truncated_time: str, e.x.{'14:59'}
            数据截断的时间
        :return:
        """
        daily_minute_num = self.get_daily_minute_num()
        temp_daily_data = self.minute_data.iloc[:daily_minute_num]
        truncated_time_index = pd.Timestamp(str(temp_daily_data.index[0].date()) + ' ' + truncated_time)
        truncated_time_index_num = np.where(temp_daily_data.index == truncated_time_index)[0][0]
        return truncated_time_index_num

def replace_zero(data, x=np.nan):
    """
    replace 0 to a predefined number for the input data
    :param data: dataframe, series or np.ndarray
        the data which contains 0
    :param x: int, float or np.nan, optional (default=np.nan)
        the value used to replace 0
    :return: same data structure as input data
        input data whose 0 has been replaced
    """
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), \
        'the data structure of input is illegal'
    data[abs(data) < 1e-8] = x
    return data

def minute_flag_check(date):
    path1 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_IC_cfg_and_mask.success'
    path2 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_spot_minute.success'
    path3 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_tick_to_minute_future_data_and_mask.success'
    path4 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_IF_cfg_and_mask.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)

_,end_date,_ = check_update_date()    
flag_root = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(end_date) + '/'
if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path_start = flag_root + str(end_date) + '_overnight_dailydata.start'
with open(flag_path_start,'w') as file:
    pass 

print('------wait minute flag')
while True:
    if minute_flag_check(end_date):
        break
    time.sleep(60)
print('flag check finished!')

print('read data')

index_data2 = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/SPOT_DATA_2020.pkl')
#index_data1 = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/SPOT_DATA_120101_200901.pkl')
index_data1 = pd.read_pickle('/dfs/group/800466/warehouse/prod/MD/CHINA_FUTURES/MINUTE/pre_history/SPOT_DATA_120101_200901.pkl')
index_data = {}
for x in index_data1.keys():
    index_data[x] = index_data1[x].combine_first(index_data2[x]).sort_index()

future_data = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/FUTURE_DATA_2020.pkl')
cfg_data_zz500 = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/IC_cfg_data_2020.pkl')
cfg_data_hs300 = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/IF_cfg_data_2020.pkl')
save_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight/OUTSAMPLE/'
if not os.path.exists(save_path):
    os.makedirs(save_path)
####################截取尾盘数据后降频至日频数据##########################

# 指数
print('start spot generate')
truncated_time_index_num = MinuteDataToDaily(index_data['amount_spot']).truncated_time_index_num('14:49')

daily_index_amount = index_data['amount_spot'].groupby(index_data['amount_spot'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum())
daily_index_close = index_data['close_spot'].groupby(index_data['close_spot'].index.date).apply(lambda _: _.iloc[truncated_time_index_num])
daily_index_open = index_data['open_spot'].groupby(index_data['open_spot'].index.date).apply(lambda _: _.iloc[0])
daily_index_high = index_data['high_spot'].groupby(index_data['high_spot'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].max())
daily_index_low = index_data['low_spot'].groupby(index_data['low_spot'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].min())
daily_index_volume = index_data['volume_spot'].groupby(index_data['volume_spot'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum())
daily_index_truely_close = index_data['close_spot'].groupby(index_data['close_spot'].index.date).apply(lambda _: _.iloc[-1])

daily_index_amount_if = index_data['amount_spot_if'].groupby(index_data['amount_spot_if'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum())
daily_index_close_if = index_data['close_spot_if'].groupby(index_data['close_spot_if'].index.date).apply(lambda _: _.iloc[truncated_time_index_num])
daily_index_open_if = index_data['open_spot_if'].groupby(index_data['open_spot_if'].index.date).apply(lambda _: _.iloc[0])
daily_index_high_if = index_data['high_spot_if'].groupby(index_data['high_spot_if'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].max())
daily_index_low_if = index_data['low_spot_if'].groupby(index_data['low_spot_if'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].min())
daily_index_volume_if = index_data['volume_spot_if'].groupby(index_data['volume_spot_if'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum())
daily_index_truely_close_if = index_data['close_spot_if'].groupby(index_data['close_spot_if'].index.date).apply(lambda _: _.iloc[-1])

daily_index_amount_ih = index_data['amount_spot_ih'].groupby(index_data['amount_spot_ih'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum())
daily_index_close_ih = index_data['close_spot_ih'].groupby(index_data['close_spot_ih'].index.date).apply(lambda _: _.iloc[truncated_time_index_num])
daily_index_open_ih = index_data['open_spot_ih'].groupby(index_data['open_spot_ih'].index.date).apply(lambda _: _.iloc[0])
daily_index_high_ih = index_data['high_spot_ih'].groupby(index_data['high_spot_ih'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].max())
daily_index_low_ih = index_data['low_spot_ih'].groupby(index_data['low_spot_ih'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].min())
daily_index_volume_ih = index_data['volume_spot_ih'].groupby(index_data['volume_spot_ih'].index.date).apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum())
daily_index_truely_close_ih = index_data['close_spot_ih'].groupby(index_data['close_spot_ih'].index.date).apply(lambda _: _.iloc[-1])

daily_index_data = {'daily_open_spot': daily_index_open, 'daily_high_spot': daily_index_high, 'daily_low_spot': daily_index_low, 
                    'daily_close_spot': daily_index_close, 'daily_truely_close_spot': daily_index_truely_close, 
                    'daily_amount_spot': daily_index_amount, 
                    'daily_volume_spot': daily_index_volume, 'daily_open_spot_if': daily_index_open_if, 
                    'daily_high_spot_if': daily_index_high_if, 'daily_low_spot_if': daily_index_low_if, 
                    'daily_close_spot_if': daily_index_close_if, 'daily_truely_close_spot_if': daily_index_truely_close_if,
                    'daily_amount_spot_if': daily_index_amount_if, 
                    'daily_volume_spot_if': daily_index_volume_if, 'daily_open_spot_ih': daily_index_open_ih, 
                    'daily_high_spot_ih': daily_index_high_ih, 'daily_low_spot_ih': daily_index_low_ih, 
                    'daily_close_spot_ih': daily_index_close_ih, 'daily_truely_close_spot_ih': daily_index_truely_close_ih,
                    'daily_amount_spot_ih': daily_index_amount_ih, 'daily_volume_spot_ih': daily_index_volume_ih}

for i_name in daily_index_data.keys():
    daily_index_data[i_name].index.name = 'dt'
    daily_index_data[i_name].index = pd.to_datetime(daily_index_data[i_name].index)

save_pickle(daily_index_data, os.path.join(save_path, 'spot_daily_overnight.pkl'))

# 期货
print('start future generate')
truncated_time_index_num = MinuteDataToDaily(future_data['amount']).truncated_time_index_num('14:49')

daily_future_amount = replace_zero(future_data['amount'].groupby(future_data['amount'].index.date).\
                                   apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum()))
daily_future_close = replace_zero(future_data['close'].groupby(future_data['close'].index.date).\
                                 apply(lambda _: _.iloc[truncated_time_index_num]))
daily_future_open = replace_zero(future_data['open'].groupby(future_data['open'].index.date).\
                                 apply(lambda _: _.iloc[0]))
daily_future_high = replace_zero(future_data['high'].groupby(future_data['high'].index.date).\
                                 apply(lambda _: _.iloc[:(truncated_time_index_num+1)].max()))
daily_future_low = replace_zero(future_data['low'].groupby(future_data['low'].index.date).\
                                 apply(lambda _: _.iloc[:(truncated_time_index_num+1)].min()))
daily_future_volume = replace_zero(future_data['volume'].groupby(future_data['volume'].index.date).\
                                   apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum()))
daily_future_truely_close = replace_zero(future_data['close'].groupby(future_data['close'].index.date).\
                                 apply(lambda _: _.iloc[-1]))

daily_future_amount_if = replace_zero(future_data['amount_if'].groupby(future_data['amount_if'].index.date).\
                                   apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum()))
daily_future_close_if = replace_zero(future_data['close_if'].groupby(future_data['close_if'].index.date).\
                                 apply(lambda _: _.iloc[truncated_time_index_num]))
daily_future_open_if = replace_zero(future_data['open_if'].groupby(future_data['open_if'].index.date).\
                                 apply(lambda _: _.iloc[0]))
daily_future_high_if = replace_zero(future_data['high_if'].groupby(future_data['high_if'].index.date).\
                                 apply(lambda _: _.iloc[:(truncated_time_index_num+1)].max()))
daily_future_low_if = replace_zero(future_data['low_if'].groupby(future_data['low_if'].index.date).\
                                 apply(lambda _: _.iloc[:(truncated_time_index_num+1)].min()))
daily_future_volume_if = replace_zero(future_data['volume_if'].groupby(future_data['volume_if'].index.date).\
                                   apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum()))
daily_future_truely_close_if = replace_zero(future_data['close_if'].groupby(future_data['close_if'].index.date).\
                                 apply(lambda _: _.iloc[-1]))

daily_future_amount_ih = replace_zero(future_data['amount_ih'].groupby(future_data['amount_ih'].index.date).\
                                   apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum()))
daily_future_close_ih = replace_zero(future_data['close_ih'].groupby(future_data['close_ih'].index.date).\
                                 apply(lambda _: _.iloc[truncated_time_index_num]))
daily_future_open_ih = replace_zero(future_data['open_ih'].groupby(future_data['open_ih'].index.date).\
                                 apply(lambda _: _.iloc[0]))
daily_future_high_ih = replace_zero(future_data['high_ih'].groupby(future_data['high_ih'].index.date).\
                                 apply(lambda _: _.iloc[:(truncated_time_index_num+1)].max()))
daily_future_low_ih = replace_zero(future_data['low_ih'].groupby(future_data['low_ih'].index.date).\
                                 apply(lambda _: _.iloc[:(truncated_time_index_num+1)].min()))
daily_future_volume_ih = replace_zero(future_data['volume_ih'].groupby(future_data['volume_ih'].index.date).\
                                   apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum()))
daily_future_truely_close_ih = replace_zero(future_data['close_ih'].groupby(future_data['close_ih'].index.date).\
                                 apply(lambda _: _.iloc[-1]))

daily_recent_month_mask = ~(replace_zero(future_data['recent_month_mask'].groupby(future_data['recent_month_mask'].index.date).sum()).isna())

daily_future_data = {'daily_open': daily_future_open, 'daily_high': daily_future_high, 'daily_low': daily_future_low, 
                     'daily_close': daily_future_close, 'daily_amount': daily_future_amount, 'daily_volume': daily_future_volume, 
                     'daily_open_if': daily_future_open_if, 'daily_high_if': daily_future_high_if, 
                     'daily_low_if': daily_future_low_if, 'daily_close_if': daily_future_close_if, 
                     'daily_amount_if': daily_future_amount_if, 'daily_volume_if': daily_future_volume_if, 
                     'daily_open_ih': daily_future_open_ih, 'daily_high_ih': daily_future_high_ih, 
                     'daily_low_ih': daily_future_low_ih, 'daily_close_ih': daily_future_close_ih, 
                     'daily_amount_ih': daily_future_amount_ih, 'daily_volume_ih': daily_future_volume_ih, 
                     'daily_recent_month_mask': daily_recent_month_mask, 'daily_turely_close': daily_future_truely_close,
                     'daily_truely_close_if': daily_future_truely_close_if, 'daily_truely_close_ih': daily_future_truely_close_ih}

for i_name in daily_future_data.keys():
    daily_future_data[i_name].index.name = 'dt'
    daily_future_data[i_name].index = pd.to_datetime(daily_future_data[i_name].index)
    
save_pickle(daily_future_data, os.path.join(save_path, 'future_daily_overnight.pkl'))

# 成分股：zz500
print('start ic cfg generate')
cfg_data = cfg_data_zz500
truncated_time_index_num = MinuteDataToDaily(cfg_data['open_zz500']).truncated_time_index_num('14:49')

daily_amount_zz500 = replace_zero(cfg_data['amount_zz500'].groupby(cfg_data['amount_zz500'].index.date).\
                                   apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum()))
daily_close_zz500 = replace_zero(cfg_data['close_zz500'].groupby(cfg_data['close_zz500'].index.date).\
                                 apply(lambda _: _.iloc[truncated_time_index_num]))
daily_open_zz500 = replace_zero(cfg_data['open_zz500'].groupby(cfg_data['open_zz500'].index.date).\
                                 apply(lambda _: _.iloc[0]))
daily_high_zz500 = replace_zero(cfg_data['high_zz500'].groupby(cfg_data['high_zz500'].index.date).\
                                 apply(lambda _: _.iloc[:(truncated_time_index_num+1)].max()))
daily_low_zz500 = replace_zero(cfg_data['low_zz500'].groupby(cfg_data['low_zz500'].index.date).\
                                 apply(lambda _: _.iloc[:(truncated_time_index_num+1)].min()))
daily_volume_zz500 = replace_zero(cfg_data['volume_zz500'].groupby(cfg_data['volume_zz500'].index.date).\
                                   apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum()))
daily_weight_zz500 = replace_zero(cfg_data['weight_zz500'].groupby(cfg_data['weight_zz500'].index.date).\
                                 apply(lambda _: _.iloc[0]))
daily_weight_mask_zz500 = ~(replace_zero(cfg_data['weight_boolean_zz500'].groupby(cfg_data['weight_boolean_zz500'].index.date).\
                                         sum()).isna())
daily_truely_close_zz500 = replace_zero(cfg_data['close_zz500'].groupby(cfg_data['close_zz500'].index.date).\
                                 apply(lambda _: _.iloc[-1]))

daily_cfg_data_ic = {'daily_open_zz500': daily_open_zz500, 'daily_high_zz500': daily_high_zz500, 
                     'daily_low_zz500': daily_low_zz500, 'daily_close_zz500': daily_close_zz500, 
                     'daily_amount_zz500': daily_amount_zz500, 'daily_volume_zz500': daily_volume_zz500, 
                     'daily_weight_zz500': daily_weight_zz500, 'daily_weight_mask_zz500': daily_weight_mask_zz500,
                     'daily_truely_close_zz500': daily_truely_close_zz500}

for i_name in daily_cfg_data_ic.keys():
    daily_cfg_data_ic[i_name].index.name = 'dt'
    daily_cfg_data_ic[i_name].index = pd.to_datetime(daily_cfg_data_ic[i_name].index)

save_pickle(daily_cfg_data_ic, os.path.join(save_path, 'ic_cfg_daily_overnight.pkl'))


# 成分股：hs300
print('start if cfg generate')
cfg_data = cfg_data_hs300
truncated_time_index_num = MinuteDataToDaily(cfg_data['open_hs300']).truncated_time_index_num('14:49')

daily_amount_hs300 = replace_zero(cfg_data['amount_hs300'].groupby(cfg_data['amount_hs300'].index.date).\
                                   apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum()))
daily_close_hs300 = replace_zero(cfg_data['close_hs300'].groupby(cfg_data['close_hs300'].index.date).\
                                 apply(lambda _: _.iloc[truncated_time_index_num]))
daily_open_hs300 = replace_zero(cfg_data['open_hs300'].groupby(cfg_data['open_hs300'].index.date).\
                                 apply(lambda _: _.iloc[0]))
daily_high_hs300 = replace_zero(cfg_data['high_hs300'].groupby(cfg_data['high_hs300'].index.date).\
                                 apply(lambda _: _.iloc[:(truncated_time_index_num+1)].max()))
daily_low_hs300 = replace_zero(cfg_data['low_hs300'].groupby(cfg_data['low_hs300'].index.date).\
                                 apply(lambda _: _.iloc[:(truncated_time_index_num+1)].min()))
daily_volume_hs300 = replace_zero(cfg_data['volume_hs300'].groupby(cfg_data['volume_hs300'].index.date).\
                                   apply(lambda _: _.iloc[:(truncated_time_index_num+1)].sum()))
daily_weight_hs300 = replace_zero(cfg_data['weight_hs300'].groupby(cfg_data['weight_hs300'].index.date).\
                                 apply(lambda _: _.iloc[0]))
daily_weight_mask_hs300 = ~(replace_zero(cfg_data['weight_boolean_hs300'].groupby(cfg_data['weight_boolean_hs300'].index.date).\
                                         sum()).isna())
daily_truely_close_hs300 = replace_zero(cfg_data['close_hs300'].groupby(cfg_data['close_hs300'].index.date).\
                                 apply(lambda _: _.iloc[-1]))

daily_cfg_data_if = {'daily_open_hs300': daily_open_hs300, 'daily_high_hs300': daily_high_hs300, 
                     'daily_low_hs300': daily_low_hs300, 'daily_close_hs300': daily_close_hs300, 
                     'daily_amount_hs300': daily_amount_hs300, 'daily_volume_hs300': daily_volume_hs300, 
                     'daily_weight_hs300': daily_weight_hs300, 'daily_weight_mask_hs300': daily_weight_mask_hs300,
                     'daily_truely_close_hs300': daily_truely_close_hs300}

for i_name in daily_cfg_data_if.keys():
    daily_cfg_data_if[i_name].index.name = 'dt'
    daily_cfg_data_if[i_name].index = pd.to_datetime(daily_cfg_data_if[i_name].index)

save_pickle(daily_cfg_data_if, os.path.join(save_path, 'if_cfg_daily_overnight.pkl'))

flag_path_success = flag_root + str(end_date) + '_overnight_dailydata.success'
with open(flag_path_success,'w') as file:
    pass