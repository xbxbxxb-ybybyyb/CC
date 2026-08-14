import numpy as np
import pandas as pd
from h5data.IO import IO

profit_pos = pd.read_hdf('/data/group/800463/tangsq/neptune/profit/20250609_a/2017_2024/zz1000_profit_interval.h5')
profit_neg = pd.read_hdf('/data/group/800463/tangsq/neptune/profit/20250609_a/2017_2024/neg/zz1000_profit_interval.h5')

for col in ['buy_vol', 'buy_vwap', 'pct_T', 'buy_tick_num', 'last_buy_time', 'target_vol', 'pct_T1', 'sell_len', 'date_list','touch_list', 'vol_list', 'Sell_ratio']:
    profit_pos[col] = np.nan
    profit_neg[col] = np.nan

IO.pd_hdf5_writer(profit_pos, hdf5='/dfs/user/023859/share_file/for_wj/neptune/20250609_a/zz1000_profit_interval_pos.h5', dataset='neptune')
IO.pd_hdf5_writer(profit_neg, hdf5='/dfs/user/023859/share_file/for_wj/neptune/20250609_a/zz1000_profit_interval_neg.h5', dataset='neptune')
