import pandas as pd
import numpy as np
from xquant.factordata import FactorData
fd = FactorData()

start_date, end_date = 20220722, 20250630
trading_days = fd.tradingday(start_date, end_date)

basic_info_future = pd.read_pickle('/dfs/group/800463/public/futures_data/IM/basicinfo/future_basicinfo.pkl')
basic_info = pd.read_pickle('/dfs/group/800463/public/option_data/000852/basicinfo/map_option_basicinfo_date.pkl')
basic_info = pd.merge(basic_info, basic_info_future[['listdate','delistdate','sname']], left_on='LastTradingDate', right_on='delistdate',how='left')
basic_info = basic_info.rename(columns={'sname':'IM_NEAR'})
basic_info['dt'] = pd.to_datetime(basic_info['dt'])
basic_info['Ticker'] = basic_info['Option']
basic_info.loc[basic_info['dt']<basic_info['listdate'],'IM_NEAR'] = np.nan
basic_info = basic_info.set_index(['dt','Ticker'])

data_2024_2025 = pd.read_excel('2024年~2025年上半年.xlsx',index_col=0)
data_2023 = pd.read_excel('事件型策略2023年净值.xlsx',index_col=0)
data_2023['策略日度盈利'] = data_2023['策略累计盈利'] - data_2023['策略累计盈利'].shift(1).fillna(0)
data_2022 = pd.DataFrame(index=[pd.Timestamp(date) for date in fd.tradingday(20220722, 20221231)],columns=['策略股票持仓','策略日度盈利'])
data = pd.concat([data_2022, data_2023[['策略股票持仓','策略日度盈利']], data_2024_2025], axis=0)
data = data.rename_axis('dt')
data.index = pd.to_datetime(data.index.astype(str))
data = data.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]

from xquant.thirdpartydata.factordata import FactorData
s = FactorData()

df = s.get_factor_value('WIND_ChinaOptionEODPrices', factors=['S_INFO_WINDCODE','TRADE_DT','S_DQ_PRESETTLE','S_DQ_SETTLE','S_DQ_OI','S_DQ_AMOUNT'],TRADE_DT='<=20250630',S_INFO_WINDCODE="like 'MO%CFE'")
df = df.rename(columns={'TRADE_DT':'dt','S_INFO_WINDCODE':'Ticker','S_DQ_PRESETTLE':'PreSettlePrice','S_DQ_SETTLE':'SettlePrice','S_DQ_AMOUNT':'amt','S_DQ_OI':'OI'})
df['Circu_Mkt'] = df['SettlePrice'] * df['OI'] * 100 / 10000
df['dt'] = pd.to_datetime(df['dt'])
df['Strike'] = df['Ticker'].apply(lambda x: int(x.split('.')[0].split('-')[-1]))
df = df.set_index(['dt','Ticker']).sort_index()
df[['LastTradingDate','IM_NEAR']] = basic_info[['LastTradingDate','IM_NEAR']]
for idx in df.index:
    dt = idx[0]
    dt_ = dt.strftime('%Y%m%d')
    Ticker = idx[1]
    Ticker_ = Ticker.split('.')[0]
    df_tick = pd.read_pickle(f'/dfs/group/800463/public/option_data/000852/tick/{Ticker_}/{dt_}.pkl')
    df_tick['MidPx'] = (df_tick['Buy1Price'] + df_tick['Sell1Price'])/2.0
    df.loc[(dt,Ticker),'twap'] = df_tick['MidPx'].mean()
    future_name = df.loc[(dt,Ticker),'IM_NEAR']
    if future_name is not np.nan:
        df_tick_future = pd.read_pickle(f'/dfs/group/800463/public/futures_data/IM/tick/{future_name}/{dt_}.pkl')
        df.loc[(dt, Ticker), 'f_twap'] = df_tick_future['LastPx'].mean()

for date in trading_days:
    data_index = pd.read_csv(f'/data/group/800080/warehouseJG/prod/LOCAL_DATA/CSV/WIND/WIND_AIndexEODPrices/{date}.csv')
    data_index_tick = pd.read_pickle(f'/dfs/group/800463/public/index_data/ZZ1000/{date}.pkl')
    data.loc[pd.Timestamp(date),'index_pre_close'] = data_index.loc[data_index['S_INFO_WINDCODE'] == '000852.SH','S_DQ_PRECLOSE'].values[0]
    data.loc[pd.Timestamp(date),'index_close'] = data_index.loc[data_index['S_INFO_WINDCODE'] == '000852.SH', 'S_DQ_CLOSE'].values[0]
    data.loc[pd.Timestamp(date),'s_twap'] = data_index_tick['LastPx'].mean()
    df.loc[df.index.get_level_values('dt')==pd.Timestamp(date),'index_pre_close'] = data_index.loc[data_index['S_INFO_WINDCODE'] == '000852.SH','S_DQ_PRECLOSE'].values[0]
    df.loc[df.index.get_level_values('dt')==pd.Timestamp(date),'s_twap'] = data_index_tick['LastPx'].mean()

df['Next_SettlePrice'] = df.groupby(['Ticker'])['SettlePrice'].shift(-1)
df['next_twap'] = df.groupby(['Ticker'])['twap'].shift(-1)
# df['pct'] = df['Next_SettlePrice']/df['SettlePrice'] - 1
df['pct'] = df['next_twap']/df['twap'] - 1
df['pct_chg'] = df['SettlePrice']/df['PreSettlePrice'] - 1

df_valuation = s.get_factor_value('WIND_ChinaOptionValuation', factors=['S_INFO_WINDCODE','TRADE_DT','W_ANAL_DELTA'], TRADE_DT='<=20250630', S_INFO_WINDCODE="like 'MO%'")
df_valuation = df_valuation.rename(columns={'TRADE_DT':'dt','S_INFO_WINDCODE':'Ticker','W_ANAL_DELTA':'delta'})
df_valuation['dt'] = pd.to_datetime(df_valuation['dt'])
df_valuation = df_valuation.set_index(['dt','Ticker']).sort_index()
df_valuation['factor_delta'] = df_valuation['delta'].groupby('Ticker').shift(1)
df['factor_delta']  = df_valuation['factor_delta']
df['delta'] = df_valuation['delta']
df = df.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]

df.to_pickle('/dfs/user/023859/options/df_MO_20220722_20250630.pkl')