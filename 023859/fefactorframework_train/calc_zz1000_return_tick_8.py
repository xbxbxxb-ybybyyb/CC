from h5data.IO import IO
import pandas as pd
import numpy as np
import decimal
from multiprocessing import Pool
from xquant.factordata import FactorData

s = FactorData()
from xquant.marketdata import MarketData

mdp = MarketData()

start_date, end_date = 20160101, 20161231
trading_days = s.tradingday(start_date, end_date)

period_dict = {
    '930_1000': ['093000000', '100000000'],
    '1000_1030': ['100000000', '103000000'],
    '1030_1100': ['103000000', '110000000'],
    '1100_1130': ['110000000', '113000000'],
    '1300_1330': ['130000000', '133000000'],
    '1330_1400': ['133000000', '140000000'],
    '1400_1430': ['140000000', '143000000'],
    '1430_1500': ['143000000', '150000000'],
}


def round_(x, n=0):
    x = x + 1e-13
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res


md = IO.read_data([start_date, end_date], columns=['pre_close', 'open', 'high', 'low', 'close', 'amt', 'adjfactor'],
                  alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3')) & (md.reset_index()['dt'] >= '2020-08-24')) | (
    md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md['ul_price'] = md['pre_close'].apply(lambda x: round_(x * 1.1, 2))
md['dl_price'] = md['pre_close'].apply(lambda x: round_(x * 0.9, 2))
md.loc[md['zcz'], 'ul_price'] = md.loc[md['zcz'], 'pre_close'].apply(lambda x: round_(x * 1.2, 2))
md.loc[md['zcz'], 'dl_price'] = md.loc[md['zcz'], 'pre_close'].apply(lambda x: round_(x * 0.8, 2))
md = md[md['amt'] > 0]


def calc_ret(date, md_date):
    stock_list = list(md_date.index.get_level_values(1).unique())
    for stock in stock_list:
        zcz = md_date.loc[(pd.to_datetime(date), stock), 'zcz']
        tick_data = mdp.get_data_by_date('stock', stock, date)
        if zcz:
            pre_close = md_date.loc[(pd.to_datetime(date), stock), 'pre_close']
            tick_data['LastPx'] = ((tick_data['LastPx'] / pre_close - 1) / 2 + 1) * pre_close
        for period in period_dict:
            tick_data_period = tick_data[
                (tick_data['MDTime'] >= period_dict[period][0]) & (tick_data['MDTime'] <= period_dict[period][1])]
            if len(tick_data_period):
                md_date.loc[(pd.to_datetime(date), stock), period] = tick_data_period['LastPx'].iloc[-1] / \
                                                                     tick_data_period['LastPx'].iloc[0] - 1
            else:
                md_date.loc[(pd.to_datetime(date), stock), period] = np.nan
    return md_date


print(start_date, end_date)

with Pool(processes=24) as pool:
    results = pool.starmap(calc_ret, [(date, md.loc[date]) for date in trading_days])

md_res = []
for result in results:
    md_res.append(result)

md_res = pd.concat(md_res)
md_res.to_pickle(f'/dfs/user/023859/neptune/20250526/scene_factors_volatility/md_{start_date}_{end_date}.pkl')