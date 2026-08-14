import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from TSmodel.MorningModel.MorningDailyUpdate.DailyUpdate import multiprocess
from dataApi.tradeDate import get_pre_trade_date, get_recent_trade_date
from dataApi.stockList import clean_stock_list, trans_int2windcode, trans_windcode2int
from functools import reduce
import pandas as pd
import numpy as np
import os

from dataApi.indName import sw_level2
from dataApi.getData import get_daily_1factor
from dataApi.sendInfo import send_file

from TSmodel.MorningModel.BackPoolRealTime2022.OLS import train_ols
from TSmodel.MorningModel.BackPoolRealTime2022.XGB import pred_xgb

gen_list = [
    "True|['WC', 'T40WC']|ts_ic_t_select|1200|0.7|True",
    "False|['WCN', 'T40WCN']|ts_ic_mean_select|1200|0.7|True",
    "True|['WCN', 'T40WCN']|group_dist_select|1200|0.7|True",
    "True|WC|ts_ret_t_select|1200|0.7|True",
]
pred_end = get_recent_trade_date()

def _func_train_model(sublist, line=0):
    res = []
    for model_gen in sublist:
        m1 = train_ols(model_gen, pred_end).set_index('code')['yh']
        m2 = pred_xgb(model_gen, pred_end).set_index('code')['yh']
        res.append((m1 + m2) / 2)
    return res

df = multiprocess(4, _func_train_model, gen_list)
df = reduce(lambda x,y:x+y, [df[j].get() for j in df])
df = reduce(lambda x,y:x+y, df)


def get_code_list(target_day):
    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, trade_mode=False,
                                  start_date=target_day, end_date=target_day)
    stock_pool = stock_pool.iloc[0][stock_pool.iloc[0]].index.to_list()
    restrict_list = pd.read_pickle(f'/data/group/800319/strategy_local_path3/daily_input/'
                                   f'{get_pre_trade_date(pred_end, -1)}/restrict_list{pred_end}.pkl')
    restrict_list = [trans_windcode2int(x) for x in restrict_list]
    code_list = sorted(list(set(stock_pool)))
    code_list = [trans_int2windcode(x) for x in code_list]
    code_list = [x for x in code_list if x[:3] not in ['688', '689']]
    code_list = sorted([trans_windcode2int(x) for x in code_list])
    code_list = sorted(list((set(code_list) - set(restrict_list))))
    return code_list


drop_code_list = pd.read_pickle(f'/data/group/800442/800319/restrict_industry/{pred_end}/drop_code_list.pkl')
code_list = sorted(list(set(get_code_list(pred_end)) - set(drop_code_list)))


df9 = df.dropna().rank(ascending=False)
df = df.dropna().rank(pct=True, ascending=False)
df = df[(df <= 0.2) & (df.index.isin(code_list))].index.to_list()
df = [trans_int2windcode(x) for x in df]

df930 = pd.read_pickle('/data/group/800442/800319/strategy_local_path/market_timing/' + '%d.pkl' % (pred_end))[1]
df930 = np.round(np.fmax((np.log(df930 / 300) + 1), 0) * 60)
df930 = df9[(df9 <= df930) & (df9.index.isin(code_list))]
df930 = df930.rank(ascending=False)
df930.index = df930.index.map(trans_int2windcode)

pd.to_pickle(df930,
             f'/data/group/800319/strategy_local_path3/morning_model/'
             f'val_sign/{get_pre_trade_date(pred_end, -1)}.pkl')
pd.to_pickle(df930, f'/data/group/800319/strategy_local_path3/morning_model/'
f'val_sign_check/{get_pre_trade_date(pred_end, -1)}.pkl')

pd.to_pickle(df, '/data/group/800442/800319/strategy_local_path/code_list_no688/' + '%d.pkl' % pred_end)
pd.to_pickle(df930,
             f'/data/group/800442/800319/strategy_local_path3/morning_model/'
             f'val_sign/{get_pre_trade_date(pred_end, -1)}.pkl')
pd.to_pickle(df930,
             f'/data/group/800442/800319/strategy_local_path3/morning_model/'
             f'val_sign_check/{get_pre_trade_date(pred_end, -1)}.pkl')

concept = pd.read_excel('/data/group/800442/800319/Concept_monitor/概念板块分工及对应个股.xlsx', index_col=0)[['概念板块', '子主题']]
sw2 = get_daily_1factor('SW2', [pred_end], df).iloc[0].map(sw_level2)
sw2.index = sw2.index.map(trans_int2windcode)
sw2.name = '申万二级行业'
# concept = pd.read_excel('/data/group/800442/800319/Concept_monitor/概念板块分工及对应个股.xlsx', index_col=0)[['概念板块', '子主题']]

concept.index.name = 'code'
concept = concept.applymap(lambda x: x + ' ')
concept = concept.groupby('code').sum()
sw2 = pd.merge(sw2, concept, left_index=True, right_index=True, how='left')
sw2.to_excel(f'/data/user/015836/dailyTrack/alphaPoolInd/股票池归属{pred_end}.xlsx')
send_file(['015836', '003186'], f'/data/user/015836/dailyTrack/alphaPoolInd/股票池归属{pred_end}.xlsx')


# num_list = sorted(os.listdir('/data/group/800442/800319/strategy_local_path/market_timing/'))
# df = pd.DataFrame([pd.read_pickle('/data/group/800442/800319/strategy_local_path/market_timing/' + x) for x in num_list])
# df['num'] = np.round(np.fmax((np.log(df[1] / 300) + 1), 0) * 60)
# df930 = pd.read_pickle('/data/group/800442/800319/strategy_local_path/market_timing/' + '%d.pkl' % (pred_end-1))[1]