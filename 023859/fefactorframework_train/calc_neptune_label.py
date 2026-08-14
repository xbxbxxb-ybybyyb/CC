import IO
import pandas as pd
import decimal
from multiprocessing import Pool
from xquant.factordata import FactorData

s = FactorData()
from xquant.marketdata import MarketData

mdp = MarketData()

start_date, end_date = 20250101, 20250331
trading_days = s.tradingday(start_date, end_date)


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


def calc_twap(date, md_date):
    stock_list = list(md_date.index.get_level_values(1).unique())
    for stock in stock_list:
        ul_price = md_date.loc[(date, stock), 'ul_price'].values[0]
        dl_price = md_date.loc[(date, stock), 'dl_price'].values[0]
        tick_data = mdp.get_data_by_date('stock', stock, date)
        tick_data_open = tick_data[(tick_data['MDTime'] > '093000000') & (tick_data['MDTime'] < '094000000')]
        tick_data_close = tick_data[(tick_data['MDTime'] > '100000000') & (tick_data['MDTime'] < '101000000')]
        buy_0930_0940_twap = tick_data_open['Sell1Price'].where(
            (tick_data_open['Sell1Price'] != 0) & (tick_data_open['Sell1Price'] > dl_price) & (
                        tick_data_open['Sell1Price'] <= ul_price)).mean()
        sell_0930_0940_twap = tick_data_open['Buy1Price'].where(
            (tick_data_open['Buy1Price'] != 0) & (tick_data_open['Buy1Price'] < ul_price) & (
                        tick_data_open['Buy1Price'] >= dl_price)).mean()
        buy_1000_1010_twap = tick_data_close['Sell1Price'].where(
            (tick_data_close['Sell1Price'] != 0) & (tick_data_close['Sell1Price'] > dl_price) & (
                        tick_data_close['Sell1Price'] <= ul_price)).mean()
        sell_1000_1010_twap = tick_data_close['Buy1Price'].where(
            (tick_data_close['Buy1Price'] != 0) & (tick_data_close['Buy1Price'] < ul_price) & (
                        tick_data_close['Buy1Price'] >= dl_price)).mean()

        md_date.loc[(pd.to_datetime(date), stock), 'buy_0930_0940_twap'] = buy_0930_0940_twap
        md_date.loc[(pd.to_datetime(date), stock), 'sell_0930_0940_twap'] = sell_0930_0940_twap
        md_date.loc[(pd.to_datetime(date), stock), 'buy_1000_1010_twap'] = buy_1000_1010_twap
        md_date.loc[(pd.to_datetime(date), stock), 'sell_1000_1010_twap'] = sell_1000_1010_twap

    return md_date


print(start_date, end_date)

with Pool(processes=24) as pool:
    results = pool.starmap(calc_twap, [(date, md.loc[date]) for date in trading_days])

md_res = []
for result in results:
    md_res.append(result)

md_res = pd.concat(md_res)
md_res.to_pickle(f'/dfs/user/023859/neptune/label_0930_0940_next_1000_1010/md_{start_date}_{end_date}.pkl')