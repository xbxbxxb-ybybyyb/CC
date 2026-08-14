# @Time : 2020/12/1 9:55
# @Author : Zhichen Lu
# @File : deal_validation.py

import pandas as pd
import numpy as np
from dataApi.getData import get_minute_1factor
import bottleneck

# pd.to_pickle([signal,pred_ret],'/data/group/800319/signal/XGB5min30BarFactorEval_ICT_signal_%d_threshold.pkl' % (int(pct_threshold * 100)))
file_name = '/data/user/015664/AFuckingTrigger/限制买入和持仓/FactorEvalRev/XBDistr5minFactor30minBar_SeperateEnsemble_InSample_UpHolding300_UpBuy100_10bp_cost.xlsx'
data = pd.read_excel(file_name,sheet_name=None)
deal_record = data['逐笔持仓统计']#pd.read_excel(file_name,sheet_name='逐笔持仓统计')
deal_stat = data['逐笔持仓综合统计']#pd.read_excel(file_name,sheet_name='逐笔持仓综合统计')
stk_list = list(set(deal_record['stk_id']))
close_adj = get_minute_1factor('close_badj',start_datetime=201601040925,end_datetime=201812281500,code_list=stk_list)
ret = close_adj.shift(-242)/close_adj - 1
rest = ret.swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]].swaplevel(0,1)

analysis = []
for start,end,cash_occupy,profit,stk in zip(deal_record['start'],deal_record['end'],deal_record['cash_occupy'],deal_record['profit'],deal_record['stk_id']):
    sell_amt = cash_occupy - profit
    ret_stk = ret[stk]
    recor_ret = ret_stk[(start//10000,start%10000)]
    analysis.append([start,end,cash_occupy,profit,stk,sell_amt,recor_ret])

analysis = pd.DataFrame(analysis,columns=['start','end','cash_occupy','profit','stk','sell_amt','ret'])
analysis['ret'] = analysis['ret'].replace(np.inf,np.nan).replace(-np.inf,np.nan)
analysis['ret'].mean()

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

stat = pd.DataFrame({'percentile_buy':percentile_buy,"percentile_sell":percentile_sell,"profit_mean_buy":profit_mean_buy,"profit_mean_sel":profit_mean_sell}).T

pct_threshold = 0.05
signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/saved_signal/XGB5min30BarFactorEval_ICT_signal_%d_threshold.pkl' % (int(pct_threshold * 100)))


from dataApi.getData import get_minute_1factor
import pandas as pd
close_adj = get_minute_1factor('close_badj',start_datetime=20160104,end_datetime=20181228,)


pct_threshold = 0.05
signal, pred_ret = pd.read_pickle('/data/group/800319/signal/XGB5min30BarFactorEval_ICT_signal_%d_threshold.pkl' % (int(pct_threshold * 100)))
signal = signal.swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]].swaplevel(0,1)
stk_list = signal.columns.tolist()
close_adj = get_minute_1factor('close_badj',start_datetime=201601040925,end_datetime=201812281500,code_list=stk_list)
ret = close_adj.shift(-242)/close_adj - 1
ret = ret.swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]].swaplevel(0,1)
signal = signal.swaplevel(0,1).loc[[1000,1030,1100,1300,1330,1400,1430]]


