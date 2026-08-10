from multiprocessing.pool import Pool
import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from os import listdir
from os.path import isfile, join
import os
import pickle
import numpy as np
import glob

#save_path = '/arch1/group/800466/warehouse/prod/MD/CHINA_STOCK/aggregated_auctions/Transaction/'
#pathlist = glob.glob('/arch1/group/800466/warehouse/prod/MD/CHINA_STOCK/pickle/Transaction/*/*.pkl')
#dlist = list(set([path.split('/')[-2] for path in pathlist]))
#for x in dlist:
#    os.makedirs(os.path.join(save_path, x))
    
pathlist = glob.glob('/arch1/group/800466/warehouse/prod/MD/CHINA_STOCK/pickle/Transaction/*/*.pkl')
EODPrices = IO.read_data([20190101, 20210616],columns=['S_DQ_PRECLOSE'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5')
EODDerivatives = IO.read_data([20190101, 20210616], columns=['FREE_SHARES_TODAY'], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5').unstack().shift().stack()
save_path = '/arch1/group/800466/warehouse/prod/MD/CHINA_STOCK/aggregated_auctions/Transaction/'

def get_data(path):
    stock = path[-13:-4]
    date = path.split('/')[-2]
    try:
        data = pd.read_pickle(path, compression='gzip').reset_index(level = 1, drop = True)
        data = data.between_time(datetime.time(9, 15), datetime.time(9, 29))
        data['MDTime'] = (data.index.strftime('%H%M%S%f').astype('int64') / 1000).astype('int64')
        data.loc[data.MDTime < 92500000,'TradeType'] = 1
        data['TradeType'] = data['TradeType'].fillna(0)
        data['TradeType'] = data['TradeType'].astype('int')
        data['pre_close'] = EODPrices.loc[(date,stock)]['S_DQ_PRECLOSE']
        data['free_shares'] = EODDerivatives.loc[(date,stock)]['FREE_SHARES_TODAY']
        data = data.sort_index().reset_index()[['MDTime','TradeIndex','TradeBuyNo','TradeSellNo','TradeType','TradeBSFlag','TradePrice','TradeQty','TradeMoney','pre_close','free_shares']]
        data.to_csv(os.path.join(save_path, date, stock + '.csv'), index = False)
    except Exception as e:
        print(path)
        print(e)
 
with Pool(24) as pool:
    pool.map(get_data, pathlist)   
