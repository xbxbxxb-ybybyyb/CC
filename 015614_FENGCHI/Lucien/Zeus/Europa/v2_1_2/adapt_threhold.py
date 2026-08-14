# coding: utf-8
# Author：fengchi863
# Date ：2023/9/26 14:21

# 测试在原来的样本上进行动态参与率设置

import pandas as pd
from Zeus.Europa.v2_0_10.path_conf import *
from dataApi.tradeDate import get_date_range, get_pre_trade_date

root_path = '/data/user/015614/Zeus/pred/Europa/v2_0_10/LgbRegModel/'

signal1 = pd.read_csv(root_path + '20191001~20200331_LgbRegModel_v1.csv')
signal2 = pd.read_csv(root_path + '20200401~20201231_LgbRegModel_v1.csv')
# signal3 = pd.read_csv(root_path + '20200401~20200930_LgbRegModel_v2.csv')
signal4 = pd.read_csv(root_path + '20201001~20210630_LgbRegModel_v2.csv').query('20210101 <= datelist <= 20210630')
signal5 = pd.read_csv(root_path + '20201001~20210331_LgbRegModel_v3.csv')
signal6 = pd.read_csv(root_path + '20210401~20211231_LgbRegModel_v3.csv').query('20210701 <= datelist <= 20211231')

concat_df = pd.concat([signal1, signal2, signal4, signal6], axis=0)

# 开始进行动态阈值调整
new_signal = pd.DataFrame()
threshold = 0.005
start_date = 20191009
end_date = 20211231
window_len = 10

cur_end_date = start_date

while cur_end_date <= end_date:
    X_train_date = start_date
    X_end_date = get_pre_trade_date(start_date, -10)
    concat_df = concat_df.query(f'{X_train_date} <= datelist <= {X_end_date}')


