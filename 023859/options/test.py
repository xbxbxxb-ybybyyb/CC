import pandas as pd
import Greeks
import math
from xquant.factordata import FactorData
fd = FactorData()

option_df = pd.read_pickle('/dfs/user/023859/options/df_MO_20220722_20250630.pkl')
for idx in option_df.index:
    dt_start = idx[0]
    dt_end = option_df.loc[idx, 'LastTradingDate']
    T = Greeks.year_fraction(dt_start, dt_end)
    if T == 0.0:
        continue
    F = option_df.loc[idx, 'f_twap']
    K = option_df.loc[idx, 'Strike']
    r = 0.0
    price = option_df.loc[idx, 'twap']
    iv = Greeks.implied_vol_b76(price,F,K,r,T,False)
    S = option_df.loc[idx, 's_twap']
    q = - math.log(F / S) / T
    delta, gamma, vega, theta = Greeks.bs_greeks_spot(S, K, r, q, T, iv, False)
    option_df.loc[idx, 'IV'] = iv
    option_df.loc[idx,'Delta'] = delta
    option_df.loc[idx,'Gamma'] = gamma
    option_df.loc[idx,'Vega'] = vega
    option_df.loc[idx,'Theta'] = theta

option_df.to_pickle('/dfs/user/023859/options/df_MO_Greeks_20220722_20250630.pkl')