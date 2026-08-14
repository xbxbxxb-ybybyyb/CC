from xquant.futuredata import FutureData
fd = FutureData()
from xquant.factordata import FactorData
s = FactorData()
'''
和tsq的函数（get_target_contract_name）核对，
'''
def get_target_contract_name(start_date=20220722, end_date=20250331):
    end_date_ = int(s.tradingday(end_date, 3)[-1])  # 按照当前算法，换仓日前一天需要触发哪个合约，换仓日后一天才知道，故仅做回测使用，实盘不行
    date_contract_dict = {}
    delivery_date = []
    tradingdays = s.tradingday(start_date, end_date_)
    for i in range(len(tradingdays)):
        date = tradingdays[i]
        print(date)
        available_contracts = fd.get_instrument_all('IM', date, date)
        last_contract = available_contracts[-1]
        date_contract_dict[date] = last_contract
        if i == 0:
            yesterday_last_contract = last_contract
            continue
        if last_contract != yesterday_last_contract:
            delivery_date.append(tradingdays[i - 1])
            date_contract_dict[tradingdays[i - 2]] = last_contract  # 交割日前一天也选择次月合约
            date_contract_dict[tradingdays[i - 1]] = last_contract  # 交割日选择次月合约

        yesterday_last_contract = last_contract

    return delivery_date, date_contract_dict

delivery_date, date_contract_dict = get_target_contract_name()

import pandas as pd
df_basic = pd.read_pickle(f'/dfs/user/015585/00_股指期货策略/Basic_future_20220801_20250430.pkl')

for tradingday in date_contract_dict.keys():
    if tradingday >= '20220801':
        res1 = date_contract_dict[tradingday]
        res2 = df_basic[df_basic['date'] == tradingday].index[0][1]
        if res1 != res2:
            print(tradingday, '有问题', res1, res2)
        else:
            print(tradingday, '1', res1, res2)

df_info = pd.read_pickle('/dfs/group/800463/data/futures_data/IM/basicinfo/future_basicinfo.pkl')