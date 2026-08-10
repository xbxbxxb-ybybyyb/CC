iw = IO.read_data([20151231,20201014], columns = ['index_weight_zz500','index_weight_hs300'], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
iw = iw.unstack().shift(1).stack()

ticker = 'IF.CFE'

pickle_path = '/data/user/012913/IndexFuture/data_center/index_stock_data/minute_data/'
tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50'}
savenamedict = {'IC.CFE':'zz500','IF.CFE':'hs300','IH.CFE':'sh50'}

def get_dt(date, hourminute):
    year = date // 10000
    month = date % 10000 // 100
    day = date % 100
    
    hourminute = hourminute // 100000
    hour = hourminute // 100
    minute = hourminute % 100
    return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))

iw_select = iw[iw[tickerdict[ticker]] > 0][[tickerdict[ticker]]]
dtlist = [str(x)[:10].replace('-','') for x in iw_select.index.get_level_values(0).unique().tolist()]

def get_datedf(date):
    iw_date_select = iw_select.loc[date].reset_index(level = 0, drop = True)
    weight_dict = iw_date_select.to_dict()[tickerdict[ticker]]

    datedflist = []
    for stock in weight_dict.keys():
        try:
            sdf = pd.read_pickle(os.path.join(pickle_path, stock, 'minute_'+ date + '.pickle')).reset_index()
        except:
            continue
        if len(sdf) != 237:
            print(stock, date, len(sdf))
            if len(sdf) == 0:
                continue
        sdf['Date'] = sdf['Date'].astype('int')
        sdf['dt'] = sdf.apply(lambda x:get_dt(x.Date, x.Time), axis = 1)
        sdf = sdf.rename(columns = {'ClosePx':'close','OpenPx':'open','HighPx':'high','LowPx':'low','Twap':'twap','Symbol':'Ticker','Volume':'volume','Turnover':'amount'})
        sdf['Ticker'] = stock
        sdf = sdf.drop(['TotalVolumeTrade','TotalValueTrade','Date','Time'], axis = 1).set_index(['dt','Ticker'])
        sdf['weight'] = round(weight_dict[stock],5)
        datedflist.append(sdf)
    return pd.concat(datedflist, axis = 0)

finaldf_list = []
with Pool(24) as pool:
    finaldf_list = pool.map(get_datedf, dtlist)
    
finaldf = pd.concat(finaldf_list, axis = 0).sort_index()
finaldf.to_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'+ticker[:2]+'_high_freq.pkl')


# 以上是把数据合并起来 后面是转换为pickle




from multifactor.IO import IO
import pandas as pd
import os
import datetime
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool
pd.set_option('max_columns', 50)
pd.set_option('max_rows', 300)
import pickle

def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
    
def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict
    
savenamedict = {'IC.CFE':'zz500','IF.CFE':'hs300','IH.CFE':'sh50'}

for ticker in ['IC.CFE','IF.CFE']:
    finaldf = pd.read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'+ticker[:2]+'_high_freq.pkl')
    fulldf = finaldf.loc[pd.to_datetime('20160506'):]
    fulldf_us = fulldf.unstack()
    data_dict = {}
    insample_data_dict = {}
    su = '_' + savenamedict[ticker][-3:]
    print(ticker, su)
    for c in tqdm(fulldf_us.columns.get_level_values(0).unique()):
        data_dict[c + su] = fulldf_us[c].sort_index()
        insample_data_dict[c + su] = data_dict[c + su].loc[pd.to_datetime('20161201'):pd.to_datetime('20200101')]

    save_pickle(insample_data_dict, '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/cfg_hf_data/'+ ticker[:2] + '_cfg_hf_insample.pkl')
    save_pickle(data_dict, '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/cfg_hf_data/'+ ticker[:2] + '_cfg_hf_160506_201014.pkl')