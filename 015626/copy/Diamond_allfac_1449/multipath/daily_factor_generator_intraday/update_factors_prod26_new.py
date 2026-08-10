import sys
sys.path.insert(4, '/data/user/017024/overnight_factors/factors/prod_26_new/')
sys.path.insert(4, './operators/')
sys.path.insert(4, './utils/')

import os
import time
# import math
# import ftplib
import pandas as pd
import numpy as np
import importlib
import datetime as dt
from multiprocessing import Pool
# from joblib import Parallel, delayed
import warnings
warnings.filterwarnings('ignore')

from factor_generator import FactorGenerator
from factor_generator_xdy import FactorGeneratorXdy
from factor_generator_complex import FactorGeneratorComplex
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from utils.date_helper import *
from multifactor.utility.dt import *




fs = [f for f in os.listdir('/data/user/017024/overnight_factors/factors/prod_26_new/') if f.endswith('.py')]
for f in fs:
    importlib.import_module(f[:-3])
    


if __name__ == '__main__':
    start_date = end_date = int(dt.datetime.now().strftime("%Y%m%d"))
    next_trading_date = get_trading_day_offset(end_date, 1)[0].strftime('%Y%m%d')
    # next_trading_date = '20210402'
    time_delta = pd.to_datetime(next_trading_date) - pd.to_datetime(str(start_date))    
    
    data = IO.read_data([20210101,20211231],columns=['PROD_ID', 'EXPIRATION_DAYS'], ftype=FType.MD,dtype=DType.FUTURES,dsource=DSource.WIND,h5root=os.path.join('/data/user/012245', 'warehouse', 'prod'))
    IC = data[data['PROD_ID']=='IC.CFE'].reset_index('Ticker')
    IC00=IC.groupby('dt').nth(0)
    ticker_now = IC00['Ticker'].iloc[-1]
    ticker_now_year = int(ticker_now[2:4])
    ticker_now_month = int(ticker_now[4:6])
    if IC00['EXPIRATION_DAYS'].iloc[-1] in [0,1,2,3]:
        if ticker_now_month == 12:
            ticker_now_year = ticker_now_year + 1
            ticker00 = str(ticker_now_year)  + '01.CF'
        else:
            ticker_now_month = ticker_now_month + 1
            if ticker_now_month < 10:
                ticker00 = str(ticker_now_year) + '0' + str(ticker_now_month) + '.CF'
            else:
                ticker00 = str(ticker_now_year) + str(ticker_now_month) + '.CF'
    else:
        ticker00 = ticker_now[2:-1]
    print('The contract traded today is: ', ticker00)
    daily_path = os.path.join('/data/user/017024/share/overnight/data/intraday/', str(end_date))
    if not os.path.exists(daily_path):
        os.makedirs(daily_path)
    pd.Series(ticker00+'E').to_csv(os.path.join(daily_path, str(end_date)+'_trading_contract.csv'))
    
    
    def minute_flag_check(date):
        path1 = os.path.join('/data/user/012245/warehouse/flags/', str(date), str(date)+'_CLOSURE.success')  # 徐博提供的指数和期货数据
        path2 = os.path.join('/data/user/017024/share/overnight/data/flag/', str(date), str(date)+'_cfg_afternoon.success')  # 下午的Wind成分股数据
        path3 = os.path.join('/data/user/015626/data/share/LOCAL_DATA/FLAG/', str(date), str(date)+'_IC_cfg_and_mask_noondata_for_overnight.success')  # 魏总提供的截止中午的zz500成分股数据
        path4 = os.path.join('/data/user/015626/data/share/LOCAL_DATA/FLAG/', str(date), str(date)+'_IF_cfg_and_mask_noondata_for_overnight.success')  # 魏总提供的截止中午的hs300成分股数据
        return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)
    
    flag_root = '/data/user/017024/data/flag/' + str(end_date) + '/'
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)
    flag_path_start = flag_root + str(end_date) + '_overnight_factors_intraday_prod_26_new.start'
    with open(flag_path_start,'w') as file:
        pass 

    print('------wait minute flag')
    while True:
        if minute_flag_check(end_date):
            break
        time.sleep(1)
    print('flag check finished!')
    

    prev_date = 20200101
    print(dt.datetime.now())
    print(prev_date, start_date, end_date)
    FactorGenerator().prepare_hot_data(prev_date, end_date)
    print(dt.datetime.now())
    subclass_list = FactorGenerator.__subclasses__()     
    print('factor count: ', len(subclass_list))
        
    for i, subcls in enumerate(subclass_list):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        try:
            subcls(savepath='/data/user/017024/share/overnight/alpha_intraday/prod_26_new').__callback__(start_date, end_date)
        except Exception as e:
            print('***********************************************************************************************************')
            print(e)
            print('***********************************************************************************************************')
        
    
    prev_date = 20200101
    print(dt.datetime.now())
    print(prev_date, start_date, end_date)
    FactorGeneratorComplex().prepare_hot_data(prev_date, end_date)
    print(dt.datetime.now())
    subclass_list = FactorGeneratorComplex.__subclasses__()     
    print('factor count: ', len(subclass_list))
        
#    for i, subcls in enumerate(subclass_list):
#        print(i+1, subcls().__class__.__name__, dt.datetime.now())
#        subcls(savepath='/data/user/017024/share/overnight/alpha_intraday/prod_26_new').__callback__(start_date, end_date)
    def func1(subcls):
        print(subcls().__class__.__name__)
        try:
            subcls(savepath='/data/user/017024/share/overnight/alpha_intraday/prod_26_new').__callback__(start_date, end_date)
        except Exception as e:
            print('***********************************************************************************************************')
            print(e)
            print('***********************************************************************************************************')
        return None
    
    print(dt.datetime.now())
    # Parallel(n_jobs=-1, max_nbytes='1G')(delayed(func1)(i) for i in subclass_list)
    with Pool() as pool:
        pool.map(func1, subclass_list)
    print(dt.datetime.now())

    
    prev_date = 20120101
    print(dt.datetime.now())
    print(prev_date, start_date, end_date)
    FactorGeneratorXdy().prepare_hot_data(prev_date, end_date)
    print(dt.datetime.now())
    subclass_list = FactorGeneratorXdy.__subclasses__()     
    print('factor count: ', len(subclass_list))
        
    for i, subcls in enumerate(subclass_list):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        try:
            subcls(savepath='/data/user/017024/share/overnight/alpha_intraday/prod_26_new').__callback__(start_date, end_date)
        except Exception as e:
            print('***********************************************************************************************************')
            print(e)
            print('***********************************************************************************************************')


    flag_path_success = flag_root + str(end_date) + '_overnight_factors_intraday_prod_26_new.success'
    with open(flag_path_success, 'w') as file:
        pass

        
    # 下面是根据因子值计算仓位
    ic_prod_path = '/data/user/017024/share/overnight/alpha_intraday/prod_26_new/'
    ic_factor_list = sorted(os.listdir(ic_prod_path))
    ic_factors = [os.path.join(ic_prod_path, i) for i in ic_factor_list]

    factor_prod = None
    for i, i_name in enumerate(ic_factors):
        factor_minute = pd.read_hdf(i_name) 
        factor_prod = factor_minute if factor_prod is None else pd.concat([factor_prod, factor_minute], axis=1)
    factor_prod = factor_prod.drop('factor_xdy', axis=1)
    
    # factor_prod = pd.concat([factor_prod.iloc[:16], factor_prod.iloc[17:]], axis=0)  # 20210305那天有的因子重复计算了，需要删除
    factor_prod[factor_prod<0.75] = np.nan
    temp1 = factor_prod.count(axis=1) / factor_prod.shape[1]
    temp2 = pd.Series(np.searchsorted([0.75, 0.8, 0.85, 0.9, 0.95, 1], factor_prod.mean(axis=1).dropna()).flatten(), 
                                        index=factor_prod.mean(axis=1).dropna().index) * 0.2 + 0.4
    temp2 = temp2.reindex(temp1.index)
    factors_signal = temp1 * temp2
    factors_signal = factors_signal.fillna(0)
    print("Today's position is: " + str(factors_signal.iloc[-1]))

    if not ((time_delta == dt.timedelta(1)) or ((time_delta == dt.timedelta(3)))):
        print('The next trading day is a holiday.')
        exit()

    df_position = pd.read_excel('/data/user/017024/position_demo.xlsx', index_col=0)
    
    today_data_future_index = pd.read_hdf(os.path.join('/data/user/012245/warehouse/prod/market/closure/', str(end_date)) + '.h5')
    ic_price = today_data_future_index[today_data_future_index['windcode']=='IC'+ticker00+'E']['close'].sort_index().iloc[-1]
    if_price = today_data_future_index[today_data_future_index['windcode']=='IF'+ticker00+'E']['close'].sort_index().iloc[-1]
    ih_price = today_data_future_index[today_data_future_index['windcode']=='IH'+ticker00+'E']['close'].sort_index().iloc[-1]
    quota_today = 55000000 * factors_signal.iloc[-1]
    
    position_list = [np.minimum(round(quota_today/(200*ic_price)), 40), np.minimum(round(quota_today/(300*if_price)), 35),\
                     np.minimum(round(quota_today/(300*ih_price)), 45)]
    ticker_list = ['IC'+ticker00[:4], 'IF'+ticker00[:4], 'IH'+ticker00[:4]]
    print(position_list)

    df_position['证券代码'] = ticker_list
    df_position['指令数量'] = position_list

    df_position.to_excel('/data/user/017024/share/overnight/data/daily_excel/Diamond_' + str(end_date) + '_PM.xlsx')
    df_position.to_excel('/data/user/013547/建仓权重文件/5160604/Diamond_' + str(end_date) + '_PM.xlsx')
    
    df_position['指令方向'] = '卖出平仓'
    df_position.to_excel('/data/user/017024/share/overnight/data/daily_excel/Diamond_' + str(next_trading_date) + '_AM.xlsx')
    df_position.to_excel('/data/user/013547/建仓权重文件/5160604/Diamond_' + str(next_trading_date) + '_AM.xlsx')

#    ftp = ftplib.FTP('168.8.2.60')
#    ftp.login('zsd', 'zsd')
#    ftp.cwd('/CYX/zhangf')
#    ftp.storbinary('STOR '+ 'Diamond_' + str(end_date) + '_PM.xlsx', open('/data/user/017024/share/overnight/data/daily_excel/Diamond_' + str(end_date) + '_PM.xlsx', 'rb'))
#    ftp.storbinary('STOR '+ 'Diamond_' + str(next_trading_date) + '_AM.xlsx', open('/data/user/017024/share/overnight/data/daily_excel/Diamond_' + str(next_trading_date) + '_AM.xlsx', 'rb'))
    # print('Ticket interval: ', str(round(240/np.max(position_list))))
    df_for_cyx = pd.DataFrame([ticker_list, [str(int(i))+ '张' for i in position_list],[str(int(240/i)) + '秒' if abs(i)>1e-8 else 'inf' for i in position_list]]).T
    print('\n')
    print('\n')
    print('\n')
    print(df_for_cyx)
    print('\n')
    print('\n')
    print('\n')

    print(dt.datetime.now())


