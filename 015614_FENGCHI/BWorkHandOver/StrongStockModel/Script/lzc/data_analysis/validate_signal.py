# @Time : 2021/3/22 16:12
# @Author : Zhichen Lu
# @File : validate_signal.py
import os
import pandas as pd
from StrongStockModel.conf.path_config import deal_price_path
from dataApi.getData import get_minute_1factor

signal,pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_LigtGBMOnly_0.05.pkl')
label = pd.read_pickle('/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl')
label = label.loc[20160104:]
res = pd.read_excel('/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEra/LigtGBMOnlyAlphaTriggerPoolV3Top600_deal_ratio_0.1_per_ratio_0.0050_threshold_0.05VolConsider_UpBuy100_10bp_cost.xlsx',sheet_name=None)
triggered_signal = res['逐笔持仓统计']
label['signal'] = False
signal_stack = signal.stack().reindex(label.index)
label['signal'] = signal_stack.fillna(False)
triggered_signal['date'] = triggered_signal['start'].apply(lambda x : x//10000)
triggered_signal['time'] = triggered_signal['start'].apply(lambda x : x%10000)
triggered_signal['year'] = triggered_signal['start']//100000000
triggered_signal = triggered_signal.set_index(['date','time','stk_id'])

triggered_signal.groupby('year').mean()['收益率']
label['triggered_signal'] = False
label.loc[triggered_signal.index,'triggered_signal'] = True

future_vol = pd.read_pickle(deal_price_path+'vol_future_rolling_30_sum.pkl').loc[20160104:20181231]
close = get_minute_1factor('close',start_datetime=20160104,end_datetime=20181231)

future_vol = future_vol.stack(dropna=False)
close = close.stack(dropna=False)

future_vol = future_vol.loc[label.index]
close = close.loc[label.index]

close = close.stack()
close = close.loc[label.index]
label['target_vol']




label['year'] = [x[0]//10000 for x in label.index]
label[label['signal']].mean()
label[label['triggered_signal']].mean()

label[label['signal']].groupby('year').mean()
label[label['triggered_signal']].groupby('year').mean()