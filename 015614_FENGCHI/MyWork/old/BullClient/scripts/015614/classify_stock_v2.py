# coding: utf-8
# Author：fengchi863
# Date ：2020/9/2 8:53

import numpy as np
import pandas as pd

from BullClient.RecordDataSet.RecordDataSet import RecordDataSet
from BullClient.conf.path_conf import stock_type_path
from BullClient.dataApi.getData import get_daily_1factor, get_date_range

rds = RecordDataSet()
deliver = rds.get_clean_deliver_data()
date_list = get_date_range(20130401, 20141231)
str_date_list = list(map(str, date_list))
close = get_daily_1factor('close_badj', date_list=date_list)

target_date_list = get_date_range(20130704, 20141231)
target_stk_list = get_daily_1factor('close', date_list=target_date_list).columns.tolist()
# 涨跌停
limit_up = get_daily_1factor('limit_up', date_list=date_list)
# 上市日期
ipo_date = get_daily_1factor('live_days', date_list=date_list)
stk_list = ipo_date.columns.tolist()
# 涨停天数
h5_path = "/data/group/wdb_h5/WIND/universe_complete/universe_complete.h5"
up_info = pd.read_hdf(h5_path, 'OPENUPLIMIT')
up_info = up_info.reset_index().pivot_table(index='dt', columns='Ticker', values='OPENUPLIMIT')
up_info.index = [int(x.strftime('%Y%m%d')) for x in up_info.index]
up_info.columns = [int(x[:-3]) for x in up_info.columns]
up_info = up_info.loc[20140101:20151231]
up_info[up_info == 0] = -1
up_info[up_info == 1] = 0
up_info[up_info == -1] = 1
# 涨停价，类型3的判断要素
deliver = rds.get_clean_deliver_data()
buy_deliver = deliver[deliver['成交数量'] == deliver['剩余股数']]
buy_price = buy_deliver.pivot_table(index='委托日期', columns='证券代码', values='成交价格')

# 类型1的判断要素
type_1_1 = (up_info.notnull().cumsum().replace(0, np.nan) <= 90) & \
           (up_info.cumprod() == 0) & \
           (ipo_date < 90)
type_1_2 = ((up_info == 1).cumsum().replace(0, np.nan) == up_info.notnull().cumsum().replace(0, np.nan))

# 复牌股
pause = get_daily_1factor('pause', date_list=date_list)
pause = pause.rolling(10).max()
pause = pause > 0.5

# 类型2
apart_ipo = ipo_date > 10
type_2 = (pause == 1) & apart_ipo


# 类型3的判断要素
high = get_daily_1factor('high', date_list=date_list)
max_px = limit_up * high
buy_price = buy_price.reindex_like(max_px)
buy_is_max = (buy_price == max_px)
type_3 = buy_is_max & (~type_1_1) & (~type_1_2) & (~type_2)

# 涨幅
pctchg = get_daily_1factor('pct_chg', date_list=date_list)
is_max_20d_4 = (close == close.rolling(20).max())

# 类型5的判断要素
net_value = (1 + pctchg).cumprod()
pre_1d_pctchg = net_value.pct_change(1)
pre_2d_pctchg = net_value.pct_change(2)
pre_3d_pctchg = net_value.pct_change(3)
pre_5d_pctchg = net_value.pct_change(5)
is_max_1d = (close.shift(1) == close.rolling(20).max())
is_max_2d = (close.shift(2) == close.rolling(20).max())
is_max_3d = (close.shift(3) == close.rolling(20).max())
is_max_5d = (close.shift(5) == close.rolling(20).max())

# 类型6的判断要素
pre_10d_max_close = close.rolling(10).max()
t_1_pctchg = close.shift(1) / pre_10d_max_close.shift(1) - 1
high_badj = get_daily_1factor('high_badj', date_list=date_list)
low_badj = get_daily_1factor('low_badj', date_list=date_list)
rolling_10_high = high_badj.shift(1).rolling(10).max()
rolling_10_low = low_badj.shift(1).rolling(10).min()
px_15_pct = rolling_10_low + 0.15 * (rolling_10_high - rolling_10_low)
under_15_pct = close.shift(1) < px_15_pct

print('类型1...')
type_1_1 = type_1_1.loc[target_date_list, target_stk_list]
type_1_1.to_pickle(stock_type_path + 'type_1_1.pkl')
type_1_2 = type_1_2.loc[target_date_list, target_stk_list]
type_1_2.to_pickle(stock_type_path + 'type_1_2.pkl')

print('类型2...')
type_2 = type_2.loc[target_date_list, target_stk_list]
type_2.to_pickle(stock_type_path + 'type_2.pkl')

print('类型3...')
type_3 = type_3.loc[target_date_list, target_stk_list]
type_3.to_pickle(stock_type_path + 'type_3.pkl')

print('类型4...')
type_4 = (pctchg > 2) & (is_max_20d_4 == True) & (~buy_is_max)
type_4 = type_4.loc[target_date_list, target_stk_list]
type_4.to_pickle(stock_type_path + 'type_4.pkl')

print('类型5...')
is_class_5_1 = (pre_1d_pctchg > 2) | \
               (pre_2d_pctchg > 2) | \
               (pre_3d_pctchg > 2) | \
               (pre_5d_pctchg > 3)
is_class_5_2 = (is_max_1d | is_max_2d | is_max_3d | is_max_5d)
type_5 = is_class_5_1 & is_class_5_2 & (pctchg < 2)
type_5 = type_5.loc[target_date_list, target_stk_list]
type_5.to_pickle(stock_type_path + 'type_5.pkl')

print('类型6...')
type_6 = (t_1_pctchg < -0.03) & under_15_pct
type_6 = type_6.loc[target_date_list, target_stk_list]
type_6.to_pickle(stock_type_path + 'type_6.pkl')

print('类型7...')
type_7 = ~(type_1_1 | type_1_2 | type_2 | type_3 | type_4 | type_5 | type_6)
type_7 = type_7.loc[target_date_list, target_stk_list]
type_7.to_pickle(stock_type_path + 'type_7.pkl')

print('类型统计完成')
