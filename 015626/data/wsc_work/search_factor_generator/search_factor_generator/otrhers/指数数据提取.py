import pandas as pd
import multifactor.utility.dt as ut

from xquant.thirdpartydata.marketdata import MarketData

ma = MarketData()

trading_days = ut.get_trading_date_range(20120101, 20210315)

df_final = None

for i_date in trading_days:
    start_time = str(int(i_date.year * 1e10 + i_date.month * 1e8 + i_date.day * 1e6 + 93000))
    end_time = str(int(i_date.year * 1e10 + i_date.month * 1e8 + i_date.day * 1e6 + 150000))
    df_temp = ma.getKLine4ZTDataFrame('000985.SH', start_time, end_time, 10, 20, True) \
        [['MDDate', 'MDTime', 'OpenPx', 'ClosePx', 'LowPx', 'HighPx', 'TotalVolumeTrade', 'TotalValueTrade']]
    df_temp['Ticker'] = pd.to_datetime([str(int(int(i) / 1000)) for i in df_temp['MDDate'] + df_temp['MDTime']])
    df_temp = df_temp.set_index('Ticker')
    df_temp = df_temp[['OpenPx', 'ClosePx', 'LowPx', 'HighPx', 'TotalVolumeTrade', 'TotalValueTrade']]
    df_temp.columns = ['open', 'close', 'low', 'high', 'volume', 'amount']
    df_final = df_temp if df_final is None else pd.concat([df_final, df_temp], axis=0)

df_final = df_final.sort_index()
