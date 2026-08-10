import os
import importlib
import datetime
import pandas as pd
import multiprocessing
import sys
sys.path.insert(0, '/data/user/000072/LYM_STOCKS/factor_list_prod_positive/')


from xquant.factordata import FactorData
s = FactorData()

today = datetime.datetime.today().strftime('%Y%m%d')
yesterday = s.tradingday(20220101, today)[-2]

univ = pd.read_pickle('/data/user/000072/LYM_STOCKS/stock_universe/universe_factors.pkl')
univ = univ[univ.dt == today]
univ_1 = univ.copy()
univ_1.dt = pd.Timestamp(yesterday)

#pa = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/Transaction/'
pa = '/data/group/800466/warehouse/prod/MD/CHINA_STOCK/Transaction/'
target_pa = '/data/user/000072/LYM_STOCKS/data/Transaction/'
for i in univ.values:
    try:
        print (i[0].strftime('%Y%m%d'), datetime.datetime.now())
        data = pd.read_csv(pa + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
        data = data.loc[data.dt < i[0].strftime('%Y-%m-%d') + ' 09:26:00']
        data.loc[(data.TradeBuyNo > data.TradeSellNo) & (data.TradeType == 0), 'TradeBSFlag'] = 1
        data.loc[(data.TradeBuyNo < data.TradeSellNo) & (data.TradeType == 0), 'TradeBSFlag'] = 2
        if not os.path.exists(target_pa + i[1]):
            os.makedirs(target_pa + i[1])
        data.to_csv(target_pa + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv', index = False)
    except:
        print(i[0].strftime('%Y%m%d %H:%M:%S'), i[1], 'cannot find arch0 file')
        
for i in univ_1.values:
    try:
        print (i[0].strftime('%Y%m%d'), datetime.datetime.now())
        data = pd.read_csv(pa + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
#        data = data.loc[data.dt < i[0].strftime('%Y-%m-%d') + ' 09:26:00']
        data.loc[(data.TradeBuyNo > data.TradeSellNo) & (data.TradeType == 0), 'TradeBSFlag'] = 1
        data.loc[(data.TradeBuyNo < data.TradeSellNo) & (data.TradeType == 0), 'TradeBSFlag'] = 2
        if not os.path.exists(target_pa + i[1]):
            os.makedirs(target_pa + i[1])
        data.to_csv(target_pa + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv', index = False)
    except:
        print(i[0].strftime('%Y%m%d %H:%M:%S'), i[1], 'cannot find arch0 file')


def calc(i):
    importlib.import_module(i)
    print (i, ' done ', datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'))

pool = multiprocessing.Pool(processes = 24)

factors = [x[:-3] for x in os.listdir('/data/user/000072/LYM_STOCKS/factor_list_prod_positive/') if x.endswith('.py')]
#factors = [x for x in factors if (int(x.strip('factor_')) >= 300) & (int(x.strip('factor_')) < 400)]

print(datetime.datetime.now(), "Sub-process(es) start.")
for i in factors:
    pool.apply_async(calc, (i, ))
    
pool.close()
pool.join()
print(datetime.datetime.now(), "Sub-process(es) done.")