import json,datetime,os,glob
from multiprocessing.pool import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import numpy as np
pd.set_option('max_columns', 200)
import glob
import bottleneck as bk

ffill_list = ['open','high','low','close','Ticker', 'adjfactor', 'float_shares','twap','weight']
nofill_list = ['AskP%d' % x for x in range(5)] + ['BidP%d' % x for x in range(5)]
fill0_list = ['amount', 'volume', 'AbsPxPath', 'Ask1AmtMean', 'AskV0', 'AskV1', 'AskV2', 'AskV3', 'AskV4', 'AskVolMean', 'Bid1AmtMean', 
              'BidAskSpreadMean', 'BidV0', 'BidV1', 'BidV2', 'BidV3', 'BidV4', 'BidVolMean', 'Buy1NumOrdersMean', 
              'BuyNumOrdersSumMean', 'BuyOrderQtySumMean', 'BuyTradeMoney', 'BuyTradeNum', 'BuyTradeQuantity', 'BuyUniqueOrderNum', 
              'PxStd', 'PxVolCorr', 'Sell1NumOrdersMean', 'SellNumOrdersSumMean', 'SellOrderQtySumMean', 'SellTradeMoney', 
              'SellTradeNum', 'SellTradeQuantity', 'SellUniqueOrderNum', 'TotalAskVol', 'TotalBidVol', 'TotalValueTrade', 
              'TotalVolumeTrade', 'VolStd', 'WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean',
              'buy_bigorder_count', 'buy_bigorder_money', 'buy_bigorder_volume', 'buy_midorder_count', 'buy_midorder_money', 
              'buy_midorder_volume', 'buy_smallorder_count', 'buy_smallorder_money', 'buy_smallorder_volume', 'buy_superorder_count', 
              'buy_superorder_money', 'buy_superorder_volume', 'sell_bigorder_count', 'sell_bigorder_money', 'sell_bigorder_volume', 
              'sell_midorder_count', 'sell_midorder_money', 'sell_midorder_volume', 'sell_smallorder_count', 'sell_smallorder_money', 
              'sell_smallorder_volume', 'sell_superorder_count', 'sell_superorder_money', 'sell_superorder_volume',  'turnover_rate']
total_columns = ffill_list + nofill_list + fill0_list

csv_rootpath = '/data/group/800466/warehouse/prod/MarketData/MD/TEMP_STOCK/'
h5_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE_v5/'

index_data_300 = IO.read_data(columns = ['close'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_INDEX/MINUTE/000300.SH.h5')
index_close_300 = index_data_300['close'].xs('000300.SH', level = 1)
index_ret_300 = index_close_300.pct_change(1, fill_method=None)


index_data_500 = IO.read_data(columns = ['close'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_INDEX/MINUTE/000905.SH.h5')
index_close_500 = index_data_500['close'].xs('000905.SH', level = 1)
index_ret_500 = index_close_500.pct_change(1, fill_method=None)

def get_index_fromdate(date):
    t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00',
                                                                                              '14:56:00',
                                                                                              freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for m in t_mins_list:
        index_list.append(str(date) + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    return index_min.set_index('dt').sort_index()

def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output
    
def get_csvdf(csvpath):
    try:
        csvdf = pd.read_csv(csvpath, index_col=[0], parse_dates=True)
    except:
        pass
    csvdf = csvdf.reindex(get_index_fromdate(date = csvpath.split('/')[-1].split('.')[0]).index)
    clist = csvdf.columns.tolist()
    res_columns = list(set(total_columns) - set(clist))
    if len(res_columns) > 0:
        for x in res_columns:
            csvdf[x] = np.nan
    csvdf[ffill_list] = csvdf[ffill_list].replace([0],np.nan).fillna(method = 'ffill')
    csvdf[fill0_list] = csvdf[fill0_list].fillna(value = 0)
#     csvdf = csvdf.reset_index()
    return csvdf

def get_stock_from_csv(stock):
    print(stock)
    csvlist = glob.glob(os.path.join(csv_rootpath, stock, '*.csv'))
    if len(csvlist) == 0:
        return
    csvdflist = []
    with Pool(24) as pool:
        csvdflist = pool.map(get_csvdf, csvlist)

    finaldf = pd.concat(csvdflist, axis = 0).sort_index()

    stk_ret = finaldf['close'].pct_change(1, fill_method=None)
    finaldf['stk_volatility'] = ts_std(stk_ret, 15)

    ret_300 = index_ret_300.reindex(stk_ret.index)
    ret_500 = index_ret_500.reindex(stk_ret.index)
    finaldf['stk_index_corr_hs300'] = stk_ret.rolling(1200, min_periods=600).corr(ret_300)
    finaldf['stk_index_corr_hs300'] = finaldf['stk_index_corr_hs300'].replace([-np.inf, np.inf], np.nan)
    finaldf['stk_index_corr_zz500'] = stk_ret.rolling(1200, min_periods=600).corr(ret_500)
    finaldf['stk_index_corr_zz500'] = finaldf['stk_index_corr_zz500'].replace([-np.inf, np.inf], np.nan)
    
    finaldf = finaldf.reset_index().set_index(['dt','Ticker'])
    h5_path = os.path.join(h5_rootpath,stock + '.h5')
    if os.path.exists(h5_path):
        IO.pd_hdf5_writer(finaldf, h5_path, dataset = stock, override = True)
    else:
        IO.pd_hdf5_writer(finaldf, h5_path, dataset = stock)
    print(stock,'done')
    
stock_list = sorted(os.listdir(csv_rootpath))
stock_list = stock_list[1000:]
for stock in stock_list:
    get_stock_from_csv(stock)
