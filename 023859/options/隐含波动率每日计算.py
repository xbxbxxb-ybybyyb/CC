import pandas as pd
import datetime
import math
from xquant.factordata import FactorData
s = FactorData()
from xquant.optiondata import OptionData
op = OptionData()
from xquant.futuredata import FutureData
fd = FutureData()
import Greeks

def pick_atm(df, win=(0.985, 1.015)): # 大约是虚四到实一
    pool = df[(df.moneyness>=win[0]) & (df.moneyness<=win[1])]
    if pool.empty: pool = df.iloc[(df.moneyness-1.0).abs().argsort()].head(3)
    return pool.iloc[(pool.moneyness-1.0).abs().argsort()].iloc[0]

today=datetime.date.today()
today = today.strftime('%Y%m%d')
last_tradingday = s.tradingday(today,-1)[0]
data_index = pd.read_csv(f'/data/group/800080/warehouseJG/prod/LOCAL_DATA/CSV/WIND/WIND_AIndexEODPrices/{last_tradingday}.csv')
index_close = data_index.loc[data_index['S_INFO_WINDCODE'] == '000852.SH','S_DQ_CLOSE'].values[0]

from xquant.thirdpartydata.factordata import FactorData
s = FactorData()
option_df = s.get_factor_value('WIND_ChinaOptionEODPrices',TRADE_DT=[f'>={last_tradingday}', f'<={last_tradingday}'],S_INFO_WINDCODE="like 'MO%'") # 取当日所有合约
option_df['dt'] = pd.to_datetime(option_df['TRADE_DT'])
option_df['Ticker'] = option_df['S_INFO_WINDCODE'].apply(lambda x: x.split('.')[0])
option_df = option_df.set_index(['dt','Ticker']).sort_index()

option_info = op.get_option_chain_symbol(date_list=[last_tradingday])
option_info = option_info[option_info['Underlying'] == '000852.SH']
option_info['dt'] = pd.to_datetime(option_info['StatusDate'])
option_info['Ticker'] = option_info['ModifiedSymbol']
option_info = option_info.set_index(['dt','Ticker'])

option_df[['LastTradingDate','StrikePrice','CallOrPut','ExpireMonth']] = option_info[['LastTradingDate','StrikePrice','CallOrPut','ExpireMonth']]
option_df['LastTradingDate'] = pd.to_datetime(option_df['LastTradingDate'])
option_df['index_close'] = index_close
option_df['tag'] = option_df.groupby('dt')['LastTradingDate'].rank(method='dense', ascending=True)
# option_df = option_df[option_df['tag'].isin([1,2])]
# for expire_month in option_df['ExpireMonth'].unique():
#     future_df = fd.get_future_data(f"IM{expire_month}.CF", f"{last_tradingday} 000000000", f"{last_tradingday} 235959999", 'K_DAY')
#     option_df.loc[(option_df['ExpireMonth'] == expire_month), 'F_SettlePrice'] = future_df['SettlePrice'].values[0]

for idx, row in option_df.iterrows(): # MO2509C5900
    dt_start = idx[0]
    contract = idx[1]
    dt_end = row['LastTradingDate']
    T = Greeks.year_fraction(dt_start, dt_end)
    if T == 0.0:
        continue
    # F = row['F_SettlePrice']
    F = row['index_close']
    K = row['StrikePrice']
    r = 0.0
    price = row['S_DQ_SETTLE']
    CallOrPut = row['CallOrPut']
    iv = Greeks.implied_vol_b76(price,F,K,r,T,CallOrPut)
    S = row['index_close']
    q = r - math.log(F / S) / T
    delta, gamma, vega, theta = Greeks.bs_greeks_spot(S, K, r, q, T, iv, CallOrPut)
    option_df.loc[idx, 'IV'] = iv
    option_df.loc[idx,'Delta'] = delta
    option_df.loc[idx,'Gamma'] = gamma
    option_df.loc[idx,'Vega'] = vega
    option_df.loc[idx,'Theta'] = theta

excel_writer = pd.ExcelWriter(f'/dfs/user/023859/share_file/for_wys/options_hedging/隐含波动率每日更新/MO_{last_tradingday}.xlsx')
for expire_month in option_df['ExpireMonth'].unique():
    option_df.loc[option_df['ExpireMonth']==expire_month].reset_index(drop=True).to_excel(excel_writer, sheet_name=f'{expire_month}')
excel_writer.save()

option_df['moneyness'] = option_df['StrikePrice'] / option_df['index_close']
atm_near_put = pick_atm(option_df[(option_df['CallOrPut'] == False) & (option_df['tag'] == 1)])

if len(atm_near_put):
    from xquant.xqutils.helper import link
    lm = link.LinkMessage()
    # lm = link.LinkMessage(['003371'])
    lm.sendMessage(f"From tsq: 今日当月平值认沽合约为{atm_near_put.S_INFO_WINDCODE}, 合约到期日为{atm_near_put.LastTradingDate.strftime('%Y%m%d')}, 隐含波动率为{atm_near_put.IV*100:.2f}%")