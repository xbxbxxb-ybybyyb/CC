from dataApi.getData import get_minute_1factor
from dataApi.tradeDate import trade_half_years
import pandas as pd

score = pd.read_hdf('/data/group/800319/市场情绪与概念板块/历史EMA市场情绪.h5', '历史EMA市场情绪').ffill().iloc[:, 0]
score = (score - score.rolling(40*242).mean()) / score.rolling(40*242).std()

close = get_minute_1factor('close', base_date=20100101, type='bench').ffill()

f1 = close.pct_change(30).shift(-31).reindex(score.index)
f2 = close.pct_change(60).shift(-61).reindex(score.index)
f3 = close.pct_change(120).shift(-121).reindex(score.index)
f4 = close.pct_change(242).shift(-243).reindex(score.index)
f5 = close.pct_change(484).shift(-485).reindex(score.index)

whole = pd.concat([f1.corrwith(score), f2.corrwith(score), f3.corrwith(score), f4.corrwith(score), f5.corrwith(score)],
                  axis=1, keys=[30, 60, 120, 240, 480])

half_years = [x for x in trade_half_years if 20130701 < x < 20210101]
half_ic = {}
for x in range(len(half_years) - 1):
    half_ic[half_years[x+1]] = pd.concat(
        [f1.loc[half_years[x]:half_years[x + 1]].corrwith(score.loc[half_years[x]:half_years[x + 1]]),
         f2.loc[half_years[x]:half_years[x + 1]].corrwith(score.loc[half_years[x]:half_years[x + 1]]),
         f3.loc[half_years[x]:half_years[x + 1]].corrwith(score.loc[half_years[x]:half_years[x + 1]]),
         f4.loc[half_years[x]:half_years[x + 1]].corrwith(score.loc[half_years[x]:half_years[x + 1]]),
         f5.loc[half_years[x]:half_years[x + 1]].corrwith(score.loc[half_years[x]:half_years[x + 1]]), ],
        axis=1, keys=[30, 60, 120, 240, 480])

half_ic = pd.concat([half_ic[x] for x in half_years[1:]], keys=half_ic.keys())

whole.to_excel('/data/user/hanxu/标准化市场情绪得分整体IC.xlsx')
half_ic.to_excel('/data/user/hanxu/标准化市场情绪得分半年IC.xlsx')