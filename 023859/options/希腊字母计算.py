import pandas as pd
import Greeks
import math
from tqdm import tqdm
from xquant.factordata import FactorData
fd = FactorData()

option_df = pd.read_pickle('/dfs/user/023859/options/df_MO_20220722_20250630.pkl')
for idx in tqdm(option_df.index):
    dt_start = idx[0]
    CallOrPut = True if idx[1].split('-')[1] == 'C' else False
    dt_end = option_df.loc[idx, 'LastTradingDate']
    T = Greeks.year_fraction(dt_start, dt_end)
    if T == 0.0:
        continue
    # F = option_df.loc[idx, 'f_twap']
    F = option_df.loc[idx, 'index_pre_close']
    K = option_df.loc[idx, 'Strike']
    r = 0.0
    # price = option_df.loc[idx, 'twap']
    price = option_df.loc[idx, 'PreSettlePrice']
    iv = Greeks.implied_vol_b76(price,F,K,r,T,CallOrPut)
    S = option_df.loc[idx, 'index_pre_close']
    # S = option_df.loc[idx, 's_twap']
    q = r - math.log(F / S) / T
    delta, gamma, vega, theta = Greeks.bs_greeks_spot(S, K, r, q, T, iv, CallOrPut)
    option_df.loc[idx, 'IV'] = iv
    option_df.loc[idx,'Delta'] = delta
    option_df.loc[idx,'Gamma'] = gamma
    option_df.loc[idx,'Vega'] = vega
    option_df.loc[idx,'Theta'] = theta

# option_df['Delta'] = option_df['Delta'].groupby('Ticker').shift(1)
# option_df['Theta'] = option_df['Theta'].groupby('Ticker').shift(1)
# option_df['Gamma'] = option_df['Gamma'].groupby('Ticker').shift(1)
# option_df['Vega'] = option_df['Vega'].groupby('Ticker').shift(1)
# option_df['IV'] = option_df['IV'].groupby('Ticker').shift(1)
option_df.to_pickle('/dfs/user/023859/options/df_MO_Greeks_20220722_20250630.pkl')