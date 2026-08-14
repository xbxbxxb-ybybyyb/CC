# @Time : 2020/12/25 14:49
# @Author : Zhichen Lu
# @File : record_stat.py

import pandas as pd
import numpy as np
from conf.path_config import deal_price_path
from tqdm import tqdm
# record = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsider/record/XGB_Linear_DTC_OutSample_deal_ratio_0.1_per_ratio_0.0050OutSample.pkl')
record = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsider/record/XGB_Linear_DTC_deal_ratio_0.1_per_ratio_0.0050InSample.pkl')
past_5day_future_30min_vol = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl')
future_30_min_vol = pd.read_pickle(deal_price_path+'vol_future_rolling_30_sum.pkl')

# target_day = 20200206
# target_day = 20200630
target_day = 20160105
past_5_day_future_vol = past_5day_future_30min_vol.loc[[target_day]].swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]].swaplevel(0,1)
acutal_future_vol = future_30_min_vol.loc[[target_day]].swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]].swaplevel(0,1)

selected_stk = []
for stk in tqdm(list(record.keys())):
    temp = record[stk]
    date_list = list(set([x[0] for x in temp.index]))
    if target_day not in date_list:
        continue
    temp = temp.loc[[target_day]]
    temp = temp[temp['flag'].isin(['B','S'])]
    if len(temp)==0:
        continue
    temp.columns = ['flag', '实际成交', '成交价', '成交后该股票持仓', '成交后当日可交易持仓', '挂单量',
       '未来可成交量上限']
    temp_past = past_5_day_future_vol[stk]
    temp_actual = acutal_future_vol[stk]
    temp['过去5日未来30分钟成交量均值'] = temp_past[temp.index]
    temp['未来30分钟该股票实际成交量'] = temp_actual[temp_past.index]
    temp = temp.reset_index()
    temp['股票代码'] = stk
    selected_stk.append(temp)

selected_stk_df = pd.concat(selected_stk)
selected_stk_df.to_excel('/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsider/record/%d.xlsx'%target_day)
