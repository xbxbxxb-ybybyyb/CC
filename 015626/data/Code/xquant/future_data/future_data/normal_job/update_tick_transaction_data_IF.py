from xquant.marketdata import MarketData

import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import numpy as np
import os
from multiprocessing import Pool
import time
from multifactor.data.utils import *

def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
    
def get_cfg_hfdata(para):
    mdp = MarketData()
        
    print(para)
    date = para[0]
    stock = para[1]
    weight = round(para[2],5)
    
    if not os.path.exists(os.path.join(rootpath, 'Tick', str(date), 'Tick_%s.pkl' % stock)):    
        tick = mdp.get_data_by_date("Stock", stock, str(date))
        if len(tick) > 0:
            tick['dt'] = tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
            tick_droplist = ['MDRecordID', 'MDReportID', 'MDDate', 'MDTime', 'MDStreamID', 'SecurityType', 'SecuritySubType', 'SecurityID',
                         'SecurityIDSource', 'Symbol', 'MDLevel', 'MDChannel', 'TradingPhaseCode', 'SwitchStatus', 'MDRecordType', 
                         'HTSCSecurityID', 'MDValidType', 'NorminalPx', 'ShortSellSharesTraded', 'ShortSellTurnover', 'ReferencePx',
                         'ComplexEventStartTime', 'ComplexEventEndTime']
            tick = tick.drop(tick_droplist, axis = 1)
            tick['Ticker'] = stock
            tick = tick.set_index(['dt','Ticker']).sort_index()
            tick.to_pickle(os.path.join(rootpath, 'Tick', str(date), 'Tick_%s.pkl' % stock), compression = 'gzip')
    
    if not os.path.exists(os.path.join(rootpath, 'Transaction', str(date), 'Transaction_%s.pkl' % stock)):  
        transaction = mdp.get_data_by_date("Transaction", stock, str(date))
        if len(transaction) > 0:
            transaction['dt'] = transaction.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
            transaction_droplist = ['MDRecordID', 'MDReportID', 'MDStreamID', 'TradingPhaseCode', 'TradeType', 'NumTrades', 
                                    'MDValidType', 'MDDate', 'MDTime', 'SecurityType', 'SecuritySubType', 'SecurityID', 
                                    'SecurityIDSource', 'Symbol', 'MDLevel', 'MDChannel', 'SwitchStatus', 'MDRecordType', 
                                    'HTSCSecurityID']
            transaction = transaction.drop(transaction_droplist, axis = 1)
            transaction['Ticker'] = stock
            transaction = transaction.set_index(['dt','Ticker']).sort_index()
            transaction.to_pickle(os.path.join(rootpath, 'Transaction', str(date), 'Transaction_%s.pkl' % stock), compression = 'gzip')
    
    if not os.path.exists(os.path.join(rootpath, 'Order', str(date), 'Order_%s.pkl' % stock)): 
        if stock.endswith('SZ'):
            order = mdp.get_data_by_date("Order", stock, str(date))
            if len(order) > 0:
                order['dt'] = order.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
                order_droplist = ['MDRecordID', 'MDReportID', 'MDDate', 'MDTime', 'MDStreamID', 'SecurityType', 'SecuritySubType', 'SecurityID',
                          'SecurityIDSource', 'Symbol', 'MDLevel', 'MDChannel', 'TradingPhaseCode', 'SwitchStatus', 'MDRecordType', 
                          'HTSCSecurityID', 'MDValidType', 'ExpirationType', 'ExpirationDays', 'Contactor', 'ContactInfo', 'ConfirmID']
                order = order.drop(order_droplist, axis = 1)
                order['Ticker'] = stock
                order = order.set_index(['dt','Ticker']).sort_index()
                order.to_pickle(os.path.join(rootpath, 'Order', str(date), 'Order_%s.pkl' % stock), compression = 'gzip')
    del(mdp)        

    

def get_target_list(ticker, startdate, enddate):
    tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50'}
    tickercolumn = tickerdict[ticker]
    indexweight = IO.read_data([startdate, enddate],columns = [tickercolumn], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    indexweight = indexweight.unstack().shift(1).stack()
    universe = indexweight[indexweight[tickercolumn]>0]
    universe = universe.reset_index()
    universe['dt'] = universe.dt.apply(lambda x:int(str(x)[:10].replace('-','')))
    return np.array(universe).tolist()

for ticker in ['IF.CFE']:
    rootpath = '/arch1/group/800466/warehouse/prod/MD/CHINA_STOCK/pickle/'

    paralist = get_target_list(ticker,20181230,20210525)

    for x in list(set([y[0] for y in paralist])):
        csvpath = os.path.join(rootpath, 'Tick', str(x))
        if not os.path.exists(csvpath):
            os.makedirs(csvpath)
        csvpath = os.path.join(rootpath, 'Transaction', str(x))
        if not os.path.exists(csvpath):
            os.makedirs(csvpath)
        csvpath = os.path.join(rootpath, 'Order', str(x))
        if not os.path.exists(csvpath):
            os.makedirs(csvpath)
            
    # download data       
    with Pool(processes = 24) as pool:
        pool.map(get_cfg_hfdata, paralist)
