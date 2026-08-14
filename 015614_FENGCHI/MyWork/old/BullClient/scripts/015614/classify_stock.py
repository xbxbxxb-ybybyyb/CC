# coding: utf-8
# Author：fengchi863
# Date ：2020/8/28 8:28

from BullClient.RecordDataSet.RecordDataSet import RecordDataSet
from BullClient.conf.path_conf import stock_type_path
from BullClient.dataApi.getData import get_daily_1factor, get_date_range

rds = RecordDataSet()
deliver = rds.get_clean_deliver_data()
date_list = get_date_range(20140101, 20151231)
str_date_list = list(map(str, date_list))
close = get_daily_1factor('close_badj', date_list=date_list)

target_date_list = get_date_range(20140401, 20151231)
target_stk_list = get_daily_1factor('close', date_list=target_date_list).columns.tolist()

# 上市日期
ipo_date = get_daily_1factor('live_days', date_list=date_list)
stk_list = ipo_date.columns.tolist()

# 复牌股
pause = get_daily_1factor('pause', date_list=date_list)
pause = pause.rolling(10).max()
pause = pause > 0.5

# 涨跌停
limit_up = get_daily_1factor('limit_up', date_list=date_list)

# 涨幅
pctchg = get_daily_1factor('pct_chg', date_list=date_list)
is_max_5d_4 = (close == close.rolling(5).max())

# 类型5的判断要素
net_value = (1 + pctchg).cumprod()
pre_1d_pctchg = net_value.pct_change(1)
pre_2d_pctchg = net_value.pct_change(2)
pre_3d_pctchg = net_value.pct_change(3)
pre_5d_pctchg = net_value.pct_change(5)
is_max_1d = (close.shift(1) == close.rolling(5).max())
is_max_2d = (close.shift(2) == close.rolling(5).max())
is_max_3d = (close.shift(3) == close.rolling(5).max())
is_max_5d = (close.shift(5) == close.rolling(5).max())

# 类型6的判断要素
is_maxupordown_3d = limit_up.shift(1).rolling(3).max()
is_5d_max_close = (close >= close.rolling(5).max()) & limit_up
is_5d_max_close_rolling_3 = is_5d_max_close.rolling(3).max()

# 类型7的判断要素
pre_10d_max_close = close.rolling(10).max()
t_1_pctchg = close.shift(1) / pre_10d_max_close.shift(1) - 1

type_1 = (ipo_date <= 90) & (ipo_date > 0)
type_1 = type_1.loc[target_date_list, target_stk_list]
type_1.to_pickle(stock_type_path + 'type_1.pkl')

apart_ipo = ipo_date > 10
type_2 = (pause == 1) & apart_ipo
type_2 = type_2.loc[target_date_list, target_stk_list]
type_2.to_pickle(stock_type_path + 'type_2.pkl')

print('start type_3...')
type_3 = (limit_up > 0.5)
type_3 = type_3.loc[target_date_list, target_stk_list]
type_3.to_pickle(stock_type_path + 'type_3.pkl')

type_4 = (pctchg > 2) & (is_max_5d_4 == True)
type_4 = type_4.loc[target_date_list, target_stk_list]
type_4.to_pickle(stock_type_path + 'type_4.pkl')

is_class_5_1 = (pre_1d_pctchg > 2) | \
               (pre_2d_pctchg > 2) | \
               (pre_3d_pctchg > 2) | \
               (pre_5d_pctchg > 3)
is_class_5_2 = (is_max_1d | is_max_2d | is_max_3d | is_max_5d)
type_5 = is_class_5_1 & is_class_5_2

type_6 = type_5 & (is_maxupordown_3d > 0.5) & (is_5d_max_close_rolling_3 > 0.5)

type_5 = type_5.loc[target_date_list, target_stk_list]
type_5.to_pickle(stock_type_path + 'type_5.pkl')
type_6 = type_6.loc[target_date_list, target_stk_list]
type_6.to_pickle(stock_type_path + 'type_6.pkl')

type_7 = (t_1_pctchg < -0.02)
type_7 = type_7.loc[target_date_list, target_stk_list]
type_7.to_pickle(stock_type_path + 'type_7.pkl')

type_8 = ~(type_1 | type_2 | type_3 | type_4 | type_5 | type_6 | type_7)
type_8 = type_8.loc[target_date_list, target_stk_list]
type_8.to_pickle(stock_type_path + 'type_8.pkl')