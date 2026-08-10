from xquant.marketdata import MarketData
from xquant.factordata import FactorData
from xquant.compute.aimr import AIMR
import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import numpy as np
import os
from multiprocessing import Pool
import time
import sys
import bottleneck as bk
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from datetime import timedelta

standard_columnslist = ['open', 'high', 'low', 'close', 'volume', 'amount', 'twap', 'Buy1NumOrdersMean', 'Sell1NumOrdersMean', 'BidAskSpreadMean', 
 'Bid1AmtMean', 'Ask1AmtMean', 'AbsPxPath', 'PxStd', 'VolStd', 'AskVolMean', 'BidVolMean', 'BuyNumOrdersSumMean', 'SellNumOrdersSumMean',
 'BuyOrderQtySumMean', 'SellOrderQtySumMean', 'WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean', 'TotalValueTrade',
 'TotalVolumeTrade', 'TotalAskVol', 'TotalBidVol', 'BidP0', 'BidV0', 'AskP0', 'AskV0', 'BidP1', 'BidV1', 'AskP1', 'AskV1', 'BidP2',
 'BidV2', 'AskP2', 'AskV2', 'BidP3', 'BidV3', 'AskP3', 'AskV3', 'BidP4', 'BidV4', 'AskP4', 'AskV4', 'PxVolCorr', 'SellTradeMoney', 
 'SellTradeQuantity', 'SellTradeNum', 'SellUniqueOrderNum', 'BuyTradeMoney', 'BuyTradeQuantity', 'BuyTradeNum', 'BuyUniqueOrderNum', 
 'sell_smallorder_count', 'sell_smallorder_money', 'sell_smallorder_volume', 'sell_midorder_count', 'sell_midorder_money',
 'sell_midorder_volume', 'sell_bigorder_count', 'sell_bigorder_money', 'sell_bigorder_volume', 'sell_superorder_count', 
 'sell_superorder_money', 'sell_superorder_volume', 'buy_smallorder_count', 'buy_smallorder_money', 'buy_smallorder_volume',
 'buy_midorder_count', 'buy_midorder_money', 'buy_midorder_volume', 'buy_bigorder_count', 'buy_bigorder_money', 'buy_bigorder_volume',
 'buy_superorder_count', 'buy_superorder_money', 'buy_superorder_volume', 'weight', 'adjfactor', 'float_shares', 'turnover_rate',
 'stk_volatility', 'stk_index_corr_hs300', 'stk_index_corr_zz500']

special_list = ['000568.SZ',
                 '000938.SZ',
                 '002032.SZ',
                 '600663.SH',
                 '601611.SH',
                 '603056.SH',
                 '603517.SH',
                 '603719.SH']

for item in special_list:
    temp = pd.read_hdf('/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE_sim2/' + item + '.h5')[standard_columnslist]
    try:
        os.remove('/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE/' + item + '.h5')
    except:
        pass
    IO.pd_hdf5_writer(temp, '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE/' + item + '.h5', dataset = item)
    print(item)