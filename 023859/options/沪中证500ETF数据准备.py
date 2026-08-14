import pandas as pd
import numpy as np
import IO
from xquant.factordata import FactorData
fd = FactorData()
from xquant.optiondata import OptionData
op = OptionData()

start_date, end_date = 20220919, 20250630
trading_days = fd.tradingday(start_date, end_date)

basic_info = pd.read_pickle('/dfs/group/800463/public/option_data/510500/basicinfo/map_option_basicinfo_date.pkl')
# basic_info = basic_info[basic_info['AdjustSign'] == 'M']
basic_info['dt'] = pd.to_datetime(basic_info['dt'])
basic_info['Ticker'] = basic_info['ModifiedSymbol']
basic_info = basic_info.set_index(['dt','Option'])

data_2024_2025 = pd.read_excel('2024年~2025年上半年.xlsx',index_col=0)
data_2023 = pd.read_excel('事件型策略2023年净值.xlsx',index_col=0)
data_2023['策略日度盈利'] = data_2023['策略累计盈利'] - data_2023['策略累计盈利'].shift(1).fillna(0)
data_2022 = pd.DataFrame(index=[pd.Timestamp(date) for date in fd.tradingday(20220919, 20221231)],columns=['策略股票持仓','策略日度盈利'])
data = pd.concat([data_2022, data_2023[['策略股票持仓','策略日度盈利']], data_2024_2025], axis=0)
data = data.rename_axis('dt')
data.index = pd.to_datetime(data.index.astype(str))
data = data.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]

from xquant.thirdpartydata.factordata import FactorData
s = FactorData()

df = s.get_factor_value('WIND_ChinaOptionEODPrices', factors=['S_INFO_WINDCODE','TRADE_DT','S_DQ_PRESETTLE','S_DQ_SETTLE','S_DQ_OI','S_DQ_AMOUNT'],TRADE_DT=['<=20250630','>=20220919'],S_INFO_WINDCODE="like '%.SH'")
df = df.rename(columns={'TRADE_DT':'dt','S_INFO_WINDCODE':'Option','S_DQ_PRESETTLE':'PreSettlePrice','S_DQ_SETTLE':'SettlePrice','S_DQ_AMOUNT':'amt','S_DQ_OI':'OI'})
# df['Circu_Mkt'] = df['SettlePrice'] * df['OI'] * 100 / 10000
df['dt'] = pd.to_datetime(df['dt'])
df = df.set_index(['dt','Option']).sort_index()
df = basic_info.join(df)

from xquant.funddata import FundData
fd = FundData()
data_index = fd.get_fund_factor_value(['510500.SH'],trading_days,['pre_close','close']).droplevel(1)
data_index.index = pd.to_datetime(data_index.index.astype(str))

for date in trading_days:
    data.loc[pd.Timestamp(date),'index_pre_close'] = data_index.loc[pd.Timestamp(date), 'pre_close']
    data.loc[pd.Timestamp(date),'index_close'] = data_index.loc[pd.Timestamp(date), 'close']
    df.loc[df.index.get_level_values('dt')==pd.Timestamp(date),'index_pre_close'] = data_index.loc[pd.Timestamp(date), 'pre_close']

for idx in df.index:
    dt = idx[0].strftime('%Y%m%d')
    Option = idx[1].split('.')[0]
    df_tick = pd.read_pickle(f'/dfs/group/800463/public/option_data/510500/tick/{Option}/{dt}.pkl')
    df.loc[idx,'twap'] = df_tick['LastPx'].mean()

df['SettlePrice_adj'] = df['SettlePrice'] * df['ContractCount']
df['twap_adj'] = df['twap'] * df['ContractCount']

df['Next_SettlePrice_adj'] = df.groupby(['Option'])['SettlePrice_adj'].shift(-1)
df['next_twap_adj'] = df.groupby(['Option'])['twap_adj'].shift(-1)

# df['pct'] = df['Next_SettlePrice']/df['SettlePrice'] - 1
df['pct'] = df['next_twap_adj']/df['twap_adj'] - 1
df['pct_chg'] = df['SettlePrice']/df['PreSettlePrice'] - 1

df_valuation = s.get_factor_value('WIND_ChinaOptionValuation', factors=['S_INFO_WINDCODE','TRADE_DT','W_ANAL_DELTA'], TRADE_DT=['<=20250630','>=20220918'], S_INFO_WINDCODE="like '%.SH'")
df_valuation = df_valuation.rename(columns={'TRADE_DT':'dt','S_INFO_WINDCODE':'Option','W_ANAL_DELTA':'delta'})
df_valuation['dt'] = pd.to_datetime(df_valuation['dt'])
df_valuation = df_valuation.set_index(['dt','Option']).sort_index()
df_valuation['factor_delta'] = df_valuation['delta'].groupby('Option').shift(1)
df['factor_delta']  = df_valuation['factor_delta']
df['delta'] = df_valuation['delta']
df = df.reset_index().set_index(['dt','Ticker'])
df = df.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]

df.to_pickle('/dfs/user/023859/options/df_510500_20220919_20250630.pkl')