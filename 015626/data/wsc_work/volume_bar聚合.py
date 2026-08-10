import pandas as pd
import numpy as np



final_df = None
N = 100

for i in range(len(trade_days)-N):
    print(i)
    temp1 = future_data_ic_remain.iloc[218*i:218*(i+N)]
    temp2 = future_data_ic_remain.iloc[218*(i+N):218*(i+N+1)]
    minute_volume = temp1['volume_normalized'].groupby(temp1.index.time).mean()
    time_stamp = np.cumsum(pd.cut(minute_volume.cumsum(), 1/(N+1) * np.arange(N+2)).value_counts().sort_index().values)
    if i != 0:
        if len(np.unique(time_stamp)) != len(time_stamp):
            time_stamp = time_stamp_copy
    time_stamp_copy = time_stamp.copy()
    for j in range(len(time_stamp)-1):
        temp3 = temp2.iloc[time_stamp[j]:time_stamp[j+1]]
        temp4 = pd.DataFrame(index=[temp3.index[-1]], columns=['open', 'close', 'high', 'low', 'amount', 'volume', 'vwap', 'twap'])
        temp4['open'] = temp3['open'][0]
        temp4['close'] = temp3['open'][-1]
        temp4['high'] = temp3['high'].max()
        temp4['low'] = temp3['open'].min()
        temp4['amount'] = temp3['amount'].sum()
        temp4['volume'] = temp3['volume'].sum()
        temp4['vwap'] = temp4['amount'] / temp4['volume']
        temp4['twap'] = temp3['twap'].mean()
        final_df = temp4 if final_df is None else final_df.append(temp4)