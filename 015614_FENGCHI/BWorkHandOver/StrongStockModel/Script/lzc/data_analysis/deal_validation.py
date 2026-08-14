# @Time : 2020/12/1 9:55
# @Author : Zhichen Lu
# @File : deal_validation.py

import pandas as pd
import numpy as np
from dataApi.getData import get_minute_1factor
import bottleneck

# file_name = '/data/user/015664/AFuckingTrigger/限制买入和持仓/FactorEvalRev/XGB_DTC20201214_SeperateEnsemble_InSample_UpHolding300_UpBuy100_5bp_threshold.xlsx'
# file_name = '/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/XGB_DTC_0.0025VolConsider_UpBuy100_10bp_cost.xlsx'
file_name = '/data/user/015664/AFuckingTrigger/限制买入和持仓/Rev240DTC/min5_NN_Comp100_param05Distr_InSample_UpHolding300_UpBuy100_10bp_cost.xlsx'
deal_record = pd.read_excel(file_name,sheet_name='逐笔持仓统计')
stk_list = list(set(deal_record['stk_id']))
amt = get_minute_1factor('amt',start_datetime=201601040925,end_datetime=201812281500,code_list=stk_list)
amt_arr = amt.values
amt_arr[np.isnan(amt_arr)] = 0
amt_arr_rolling_sum = bottleneck.move_sum(amt_arr, 30, axis=0)
amt_rolling_sum = pd.DataFrame(amt_arr_rolling_sum,index=amt.index,columns=amt.columns).shift(-30)
amt_rolling_sum = amt_rolling_sum.swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]].swaplevel(0,1)

analysis = []
for start,end,cash_occupy,profit,stk in zip(deal_record['start'],deal_record['end'],deal_record['cash_occupy'],deal_record['profit'],deal_record['stk_id']):
    sell_amt = cash_occupy - profit
    amt_stk = amt_rolling_sum[stk]
    start_amt,end_amt = amt_stk[(start//10000,start%10000)],amt_stk[(end//10000,end%10000)]
    analysis.append([start,end,cash_occupy,profit,stk,sell_amt,start_amt,end_amt])

analysis = pd.DataFrame(analysis,columns=['start','end','cash_occupy','profit','stk','sell_amt','start_amt','end_amt'])
analysis['buy_amt_ratio'] = analysis['cash_occupy']/analysis['start_amt']
analysis['sell_amt_ratio'] = analysis['sell_amt']/analysis['end_amt']


analysis['profit_ratio'] = analysis['profit']/analysis['cash_occupy']
analysis_drop_inf = analysis.replace(np.inf,np.nan)


percentile_buy = {}
percentile_sell = {}
profit_mean_buy = {}
profit_mean_sell = {}

for pct in list(range(5,100,5))+[96,97,98,99,99.9,99.99]:
    percentile_buy[pct] = analysis_drop_inf['buy_amt_ratio'].quantile(pct*0.01)
    percentile_sell[pct] = analysis_drop_inf['sell_amt_ratio'].quantile(pct*0.01)
    profit_mean_buy[pct] = analysis_drop_inf[analysis_drop_inf['buy_amt_ratio']>percentile_buy[pct]]['profit_ratio'].mean()
    profit_mean_sell[pct] = analysis_drop_inf[analysis_drop_inf['sell_amt_ratio']>percentile_buy[pct]]['profit_ratio'].mean()

#
# length = 5
# percentile_buy = pd.Series(percentile_buy).apply(lambda x : round(x,length))
# percentile_sell = pd.Series(percentile_sell).apply(lambda x : round(x,length))
#
# analysis_drop_inf['buy_amt_ratio'] = analysis_drop_inf['buy_amt_ratio'].apply(lambda x : round(x,length))
# analysis_drop_inf['sell_amt_ratio'] = analysis_drop_inf['sell_amt_ratio'].apply(lambda x : round(x,length))
# corresponding_buy_record = analysis_drop_inf[analysis_drop_inf['buy_amt_ratio'].isin(percentile_buy)].sort_values('buy_amt_ratio')
# corresponding_buy_record = pd.merge(corresponding_buy_record,pd.DataFrame({'分位数':percentile_buy}).reset_index(),
#                  left_on='buy_amt_ratio',right_on='分位数').rename(columns={'index':'分位值'})
#
# corresponding_sell_record = analysis_drop_inf[analysis_drop_inf['sell_amt_ratio'].isin(percentile_sell)].sort_values('sell_amt_ratio')
# corresponding_sell_record = pd.merge(corresponding_sell_record,pd.DataFrame({'分位数':percentile_sell}).reset_index(),
#                  left_on='sell_amt_ratio',right_on='分位数').rename(columns={'index':'分位值'})

extreme_buy_record = analysis_drop_inf[analysis_drop_inf['buy_amt_ratio']>=percentile_buy[99]].sort_values('buy_amt_ratio')
extreme_sell_record = analysis_drop_inf[analysis_drop_inf['sell_amt_ratio']>=percentile_sell[99]].sort_values('sell_amt_ratio')

stat = pd.DataFrame({'percentile_buy':percentile_buy,"percentile_sell":percentile_sell,"profit_mean_buy":profit_mean_buy,"profit_mean_sel":profit_mean_sell}).T

with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/限制买入和持仓/InitialCashBased/成交统计_min5_NN_param05.xlsx') as writer:
    stat.T.to_excel(writer,sheet_name='总体统计')
    extreme_buy_record.to_excel(writer,sheet_name='极端买入交易')
    extreme_sell_record.to_excel(writer,sheet_name='极端卖出交易')
writer.close()

pct_threshold = 0.05
signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/saved_signal/XGB5min30BarFactorEval_ICT_signal_%d_threshold.pkl' % (int(pct_threshold * 100)))
signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/saved_signal/XGBFactorEval_ic_all_t_train200_test10_factor_num100_norm_window_40.pkl')
pd.to_pickle([signal, pred_ret],'/data/group/800319/signal/XGBFactorEval_ic_all_t_train200_test10_factor_num100_norm_window_40.pkl')
from dataApi.getData import get_minute_1factor
close_adj = get_minute_1factor('close_badj',start_datetime=20160104,end_datetime=20181228,)

