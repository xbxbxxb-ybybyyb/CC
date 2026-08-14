# @Time : 2020/11/17 10:20
# @Author : Zhichen Lu
# @File : record_info_anlysis.py
import pandas as pd
from dataApi.tradeDate import get_date_range
from dataApi.getData import get_minute_1factor
import itertools
from multiprocessing import Pool,Manager
record = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/敏感性分析/record/twap_10min_record_insample_lr_XGB_NN.pkl')
stk_list = list(record.keys())
record = Manager().dict(record)
date_list = get_date_range(20160101,20181231)
time_list = [1000,1030,1100,1300,1330,1400,1430]
index_list = pd.MultiIndex.from_tuples(list(itertools.product(date_list,time_list)))
holding = Manager().dict()

def get_stk_holding(stk):
    holding[stk] = record[stk]['holding'].reindex(index_list)
    print(stk)
    return True
bool_dict = {}
pool = Pool(20)
for stk in stk_list:
    bool_dict[stk] = pool.apply_async(get_stk_holding,(stk,))
pool.close()
pool.join()

for stk in bool_dict:
    bool_dict[stk].get()
pd.to_pickle(holding._getvalue(),'/data/user/015664/AFuckingTrigger/限制买入和持仓/敏感性分析/record/twap_10min_holding_insample_lr_XGB_NN.pkl')

holding = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/敏感性分析/record/twap_10min_holding_insample_lr_XGB_NN.pkl')
holding_df = pd.concat(holding,axis=1).sort_index(axis=1).fillna(method='pad')
close = get_minute_1factor('close',start_datetime=date_list[0],end_datetime=date_list[-1])
close = close.swaplevel(0,1).loc[time_list].swaplevel(0,1)[holding_df.columns]
holding_amt = holding_df.mul(close)

