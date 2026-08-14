import pandas as pd
import json
from multiprocessing import Pool
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()

# 计算多空规模
start_date, end_date = 20200701, 20241231

def calc_sc_ul_position(date, stock_list, df_zz1000_weight, total_amt=5e8):
    res_ul = 0
    res_dl = 0
    res_stock_dict = {date:{'ul':[],'dl':[]}}
    
    df_zz1000_weight['amt'] = total_amt * df_zz1000_weight['weight'] / 100
    df_zz1000_weight = df_zz1000_weight.set_index('stock')
    for stock in stock_list:
        tick_data = mdp.get_data_by_date('stock',stock,date)
        tick_data = tick_data[tick_data['MDTime'] < '143000000']
        last_not_ul_time = tick_data[tick_data['LastPx'] != tick_data['MaxPx']]['MDTime'].iloc[-1]
        last_not_dl_time = tick_data[tick_data['LastPx'] != tick_data['MinPx']]['MDTime'].iloc[-1]
        if last_not_ul_time < '140000000':
            res_stock_dict[date]['ul'].append(stock)
            res_ul += df_zz1000_weight.loc[stock,'amt']
        if last_not_dl_time < '140000000':
            res_stock_dict[date]['dl'].append(stock)
            res_dl -= df_zz1000_weight.loc[stock,'amt']
    return pd.DataFrame([[res_ul,res_dl]],index=[date],columns=['sc_ul','sc_dl']), res_stock_dict

basic_df = pd.read_pickle('/dfs/user/023859/neptune/20250526/basic_file_zz1000_20170110_20250331.pkl')
basic_df_sc = pd.read_pickle('/dfs/user/023859/neptune/20250609/basic_file_zz1000_sc_20170110_20241231.pkl')

trading_days = s.tradingday(start_date, end_date)

with Pool(processes=24) as pool:
    results = pool.starmap(calc_sc_ul_position, [(date, list(set(basic_df.xs(pd.Timestamp(date),0).index)-set(basic_df_sc.xs(pd.Timestamp(date),0).index)), s.hset('INDEX', date, 'ZZ1000', weightType=1)) for date in trading_days])

res_df = []
res_detail = {}
for res in results:
    res_df.append(res[0])
    res_detail.update(res[1])

res_df = pd.concat(res_df)
res_df = res_df.rename_axis('dt')
res_df.index = pd.to_datetime(res_df.index.astype(str))

res_df.to_pickle(f'/dfs/user/023859/neptune/sc_udl_amt_{start_date}_{end_date}.pkl')
with open(f'/dfs/user/023859/neptune/sc_udl_detail_{start_date}_{end_date}.json','w') as f:
    json.dump(res_detail, f)