# @Time : 2020/12/30 8:57
# @Author : Zhichen Lu
# @File : FutureLimitUpDownStat.py

import pandas as pd
import os
from dataApi.getData import get_minute_1factor
from dataApi.usefulTools import arr2frame,frame2arr,ts_sum
import numpy as np

path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBasedVolConsider/'

# tag = 'In'
# close_adj = get_minute_1factor('close_badj',start_datetime=20160104,end_datetime=20181228)
# res = pd.read_excel(path+'XGB_Linear_DTC_deal_ratio_0.1_per_ratio_0.0050VolConsider_UpBuy100_10bp_cost.xlsx',sheet_name=None)

tag = 'Out'
res = pd.read_excel(path+'XGB_Linear_DTC_OutSample_deal_ratio_0.1_per_ratio_0.0050VolConsider_UpBuy100_10bp_cost.xlsx',sheet_name=None)
close_adj = get_minute_1factor('close_badj',start_datetime=20190101,end_datetime=20201030)




record_detail = res['逐笔持仓统计']
stk_list = list(set(record_detail['stk_id']))

close_adj_arr = frame2arr(close_adj)
pre_close = close_adj_arr[-2]
pre_close[1:] = pre_close[:-1]
pre_close[0] = np.nan
daily_high = np.nanmax(close_adj_arr,axis=0)
daily_low = np.nanmin(close_adj_arr,axis=0)

pct_change_to_preclose = close_adj_arr/pre_close - 1

limitup = (pct_change_to_preclose>0.098)&((close_adj_arr-daily_high)==0)
limitdown = (pct_change_to_preclose<-0.098)&((close_adj_arr-daily_low)==0)

limitup_30min = ts_sum(limitup,30)
limitup_30min[:-30] = limitup_30min[30:]
limitup_30min[-30:] = np.nan
limitdown_30min = ts_sum(limitdown,30)
limitdown_30min[:-30] = limitdown_30min[30:]
limitdown_30min[-30:] = np.nan

limitdown_30min_df = arr2frame(limitdown_30min,index=close_adj.index,columns=close_adj.columns)
limitup_30min_df = arr2frame(limitup_30min,index=close_adj.index,columns=close_adj.columns)


limitdown_30min_df = limitdown_30min_df.swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]].swaplevel(0,1)
limitup_30min_df = limitup_30min_df.swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]].swaplevel(0,1)

limitup_30min_df.index = [x[0]*10000+x[1] for x in limitup_30min_df.index]
limitdown_30min_df.index = [x[0]*10000+x[1] for x in limitdown_30min_df.index]

limitup_30min_df_stack = limitup_30min_df.stack().to_frame().rename(columns={0:'买入时点未来30分钟涨停分钟bar数量'}).reset_index()
limitdown_30min_df_stack = limitdown_30min_df.stack().to_frame().reset_index().rename(columns={0:'卖出时点未来30分钟跌停分钟bar数量'})

record_detail = pd.merge(record_detail,limitup_30min_df_stack,'left',left_on=['start','stk_id'],right_on=['level_0','level_1'])
record_detail = record_detail.drop(['level_0','level_1'],axis=1)
record_detail = pd.merge(record_detail,limitdown_30min_df_stack,'left',left_on=['end','stk_id'],right_on=['level_0','level_1'])#.drop(['level_0','level_1'],axis=1)
record_detail = record_detail.drop(['level_0','level_1'],axis=1)

# record_detail = record_detail.sort_values('买入时点未来30分钟涨停分钟bar数量',ascending=False)

record_detail.to_excel('/data/user/015664/AFuckingTrigger/RecordStat/交易未来盘中涨停数量统计%s.xlsx'%tag)
#
pct_change_to_preclose_df = arr2frame(pct_change_to_preclose,index=close_adj.index,columns=close_adj.columns)
# stat = pd.DataFrame()
record_detail[record_detail['买入时点未来30分钟涨停分钟bar数量']>0]['收益率'].shape[0],\
record_detail[record_detail['买入时点未来30分钟涨停分钟bar数量']>0]['收益率'].shape[0]/record_detail.shape[0],\
record_detail[record_detail['买入时点未来30分钟涨停分钟bar数量']>0]['收益率'].mean()
record_detail[record_detail['卖出时点未来30分钟跌停分钟bar数量']>0]['收益率'].shape[0]/record_detail.shape[0],\
record_detail[record_detail['卖出时点未来30分钟跌停分钟bar数量']>0]['收益率'].shape[0],\
record_detail[record_detail['卖出时点未来30分钟跌停分钟bar数量']>0]['收益率'].mean()
check_stk = limitup_30min_df[300552].loc[201904161000]


#
# pct_check = pct_change_to_preclose_df[:242*10][603988]
# close_adj_check = close_adj[:10*242][603988]
#
# check_stk_close = get_minute_1factor('close_badj',20160105,20160106,code_list=[603988])