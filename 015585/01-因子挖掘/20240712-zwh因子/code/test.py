import pandas as pd
import os
import datetime
import IO

df = pd.read_hdf('/dfs/user/022325/shares/qyh/pred.h5')
df = df.reset_index().sort_values(['dt','Ticker']).set_index(['dt','Ticker'])
start_date = 20200101
end_date = 20210131
df_wind = IO.read_data([start_date, end_date],
                      columns=['pct_chg'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
for col in df.columns:
    df_wind[col] = df[col].unstack().shift(2).stack()
    res_ic_day = df_wind.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))][['signal', 'pct_chg']] \
        .groupby('dt').apply(lambda x: x.corr(method='spearman').iloc[0, 1]).mean()
    print(res_ic_day)


def duplicates(lst):
    return [lst.count(x) > 1 for x in lst]