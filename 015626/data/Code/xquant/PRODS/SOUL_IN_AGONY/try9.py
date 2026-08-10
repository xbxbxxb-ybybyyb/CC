import pandas as pd
import os
di = pd.read_pickle('/data/user/016700/Data/Factors/TEMP/commodities/minute_backtest_reference_1min.pkl')

try:
    os.makedirs('/data/user/016700/Data/Factors/TEMP/commodities/minute_backtest_references/')
except:
    pass

for key in di:
    di[key].to_csv('/data/user/016700/Data/Factors/TEMP/commodities/minute_backtest_references/' + key + '.csv')