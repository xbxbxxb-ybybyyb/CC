import sys
sys.path.insert(4,'/data/user/015626/JupyterNotebooks/utils/')
from KZZ_Factor_Test import *
import json,datetime,os,glob
from multiprocessing import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import numpy as np
pd.set_option('max_columns', 200)
import glob
import bottleneck as bk
from operators_wyc import *
from tqdm import tqdm
from multifactor.data.utils import *

from xquant.marketdata import MarketData

freq = 500
opentime = '092500000'
name_dict = {'hs300': '000300.SH', 'zz500': '000905.SH', 'sz50': '000016.SH'}
weight_name_dict = {'hs300':'index_weight_hs300','zz500':'index_weight_zz500','sz50':'index_weight_sh50'}
future_name_dict={'hs300':'IF.CFE','zz500':'IC.CFE','sz50':'IH.CFE'}

columns_list = ['amount', 'volume', 'total_order_count', 'buy_amount', 'buy_volume', 'buy_order_count', 'buy_unique_order_count', 
                'buy_smallorder_count', 'buy_smallorder_money', 'buy_midorder_count', 'buy_midorder_money', 'buy_bigorder_count', 
                'buy_bigorder_money', 'buy_superorder_count', 'buy_superorder_money', 'sell_amount', 'sell_volume', 'sell_order_count', 
                'sell_unique_order_count', 'sell_smallorder_count', 'sell_smallorder_money', 'sell_midorder_count', 'sell_midorder_money'
                , 'sell_bigorder_count', 'sell_bigorder_money', 'sell_superorder_count', 'sell_superorder_money']

prod_data_path = '/data/group/800080/warehouse/prod/'
divdata = IO.read_data(alt=os.path.join(prod_data_path, 'DATABASE', 'WIND', 'AShareDividend', 'AShareDividend.h5')).reset_index()[['Ticker', 'CASH_DVD_PER_SH_PRE_TAX', 'EX_DT']]
divdata['dt'] = pd.to_datetime(divdata['EX_DT'], format="%Y%m%d")
divdata = divdata[['dt', 'Ticker', 'CASH_DVD_PER_SH_PRE_TAX']].dropna().set_index(['dt', 'Ticker'])

def get_time_df(cur_date):
    future_name = future_name_dict[index_name]
    recent_future = IO.read_data([cur_date], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
    recent_future = recent_future.xs(future_name, level = 1)['contract_00'].tolist()[0]
    futures_data = pd.read_csv('/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE/%s/%s.csv' % (recent_future[:6], str(cur_date)))
    if not os.path.exists(os.path.join(future_savepath, str(cur_date)+'.csv')):
        futures_data.to_csv(os.path.join(future_savepath, str(cur_date)+'.csv'), index = False)
    futures_data['MDTime'] = pd.to_datetime(futures_data['dt']).apply(lambda x: x.strftime('%H%M%S%f'))
    drift_temp = futures_data[(futures_data.MDTime > '1000') & (futures_data.MDTime < '1100')].MDTime.tolist()
    drift = str(min([int(x[6]) for x in drift_temp]))  # 1表示从100ms开始
    time_df = pd.DataFrame()
    t1 = pd.Series(pd.date_range(start='9:20:00.' + drift, end='11:30', freq=str(freq) + 'L').strftime('%H%M%S%f')).apply(
        lambda x: x[:-3])
    if drift == 0:
        drift = '5'
    t2 = pd.Series(pd.date_range(start='13:00:00.' + drift, end='15:01', freq=str(freq) + 'L').strftime('%H%M%S%f')).apply(
        lambda x: x[:-3])
    time_df['MDTime'] = t1.append(t2)
    time_df['index'], time_df['TradePrice'], time_df['TradeAmt'], time_df['flag'] = -1, np.nan, np.nan, 1
    time_df['dt'] = time_df['MDTime']
    return time_df

def get_stk(para):
    stk = para[0]
    cur_date = para[1]
    
    mdp = MarketData()
    df = mdp.get_data_by_date("Transaction", stk, str(cur_date))
    del(mdp)
    
    if len(df) == 0:# 停牌
        price = pd.Series(md_index_wt.xs(stk, level = 1)['pre_close'].values[0], index = time_df_index)
        price = price.to_frame()
        price.columns = [stk]
        
        result = pd.DataFrame(0, columns=columns_list, index = time_df_index)
        return [price, result]
    else:
        use_df = df.reset_index()[['index', 'MDTime', 'TradePrice', 'TradeQty', 'TradeBSFlag','TradeType','TradeBuyNo','TradeSellNo']]  # 筛选出成交数据
        use_df['amount'] = use_df['TradePrice'] * use_df['TradeQty']
        use_df['flag'] = 0
        merge_df = pd.concat([use_df, time_df]).sort_values(['MDTime', 'index'])
        merge_df['dt'] = merge_df['dt'].fillna(method = 'bfill')
        merge_df = merge_df[merge_df.flag == 0]
        deal_df = merge_df[merge_df.TradeType == 0]
        buy_deal_df = deal_df[deal_df.TradeBSFlag == 1]
        buyorder_money = buy_deal_df.groupby(['dt','TradeBuyNo'])['amount'].sum().reset_index()
        buy_small_order = buyorder_money[buyorder_money.amount <= 40000]
        buy_mid_order = buyorder_money[(buyorder_money.amount > 40000) & (buyorder_money.amount <= 200000)]
        buy_big_order = buyorder_money[(buyorder_money.amount > 200000) & (buyorder_money.amount <= 1000000)]
        buy_super_order = buyorder_money[(buyorder_money.amount > 1000000)]

        sell_deal_df = deal_df[deal_df.TradeBSFlag == 2]
        sellorder_money = sell_deal_df.groupby(['dt','TradeSellNo'])['amount'].sum().reset_index()
        sell_small_order = sellorder_money[sellorder_money.amount <= 40000]
        sell_mid_order = sellorder_money[(sellorder_money.amount > 40000) & (sellorder_money.amount <= 200000)]
        sell_big_order = sellorder_money[(sellorder_money.amount > 200000) & (sellorder_money.amount <= 1000000)]
        sell_super_order = sellorder_money[(sellorder_money.amount > 1000000)]


        # 聚合逻辑
        price = deal_df.groupby('dt')['TradePrice'].last().reindex(time_df_index)
        amount = deal_df.groupby('dt')['amount'].sum().reindex(time_df_index)
        volume = deal_df.groupby('dt')['TradeQty'].sum().reindex(time_df_index)
        total_order_count = deal_df.groupby('dt')['TradeQty'].count().reindex(time_df_index)

        # 主买
        buy_amount = buy_deal_df.groupby('dt')['amount'].sum().reindex(time_df_index)
        buy_volume = buy_deal_df.groupby('dt')['TradeQty'].sum().reindex(time_df_index)
        buy_order_count = buy_deal_df.groupby('dt')['TradeQty'].count().reindex(time_df_index)
        buy_unique_order_count = buyorder_money.groupby('dt')['amount'].count().reindex(time_df_index)
        buy_smallorder_count = buy_small_order.groupby('dt')['amount'].count().reindex(time_df_index)
        buy_smallorder_money = buy_small_order.groupby('dt')['amount'].sum().reindex(time_df_index)
        buy_midorder_count = buy_mid_order.groupby('dt')['amount'].count().reindex(time_df_index)
        buy_midorder_money = buy_mid_order.groupby('dt')['amount'].sum().reindex(time_df_index)
        buy_bigorder_count = buy_big_order.groupby('dt')['amount'].count().reindex(time_df_index)
        buy_bigorder_money = buy_big_order.groupby('dt')['amount'].sum().reindex(time_df_index)
        buy_superorder_count = buy_super_order.groupby('dt')['amount'].count().reindex(time_df_index)
        buy_superorder_money = buy_super_order.groupby('dt')['amount'].sum().reindex(time_df_index)

        # 主卖
        sell_amount = sell_deal_df.groupby('dt')['amount'].sum().reindex(time_df_index)
        sell_volume = sell_deal_df.groupby('dt')['TradeQty'].sum().reindex(time_df_index)
        sell_order_count = sell_deal_df.groupby('dt')['TradeQty'].count().reindex(time_df_index)
        sell_unique_order_count = sellorder_money.groupby('dt')['amount'].count().reindex(time_df_index)
        sell_smallorder_count = sell_small_order.groupby('dt')['amount'].count().reindex(time_df_index)
        sell_smallorder_money = sell_small_order.groupby('dt')['amount'].sum().reindex(time_df_index)
        sell_midorder_count = sell_mid_order.groupby('dt')['amount'].count().reindex(time_df_index)
        sell_midorder_money = sell_mid_order.groupby('dt')['amount'].sum().reindex(time_df_index)
        sell_bigorder_count = sell_big_order.groupby('dt')['amount'].count().reindex(time_df_index)
        sell_bigorder_money = sell_big_order.groupby('dt')['amount'].sum().reindex(time_df_index)
        sell_superorder_count = sell_super_order.groupby('dt')['amount'].count().reindex(time_df_index)
        sell_superorder_money = sell_super_order.groupby('dt')['amount'].sum().reindex(time_df_index)

        if use_df['MDTime'].min() >= '093000000':  # 若集合竞价期间无成交记录，用前收盘价代替集合竞价开盘价
            price.iloc[0] = md_index_wt.xs(stk, level = 1)['pre_close'].values[0]
            
        rlist = [amount, volume, total_order_count, buy_amount, buy_volume, buy_order_count, buy_unique_order_count, 
                 buy_smallorder_count, buy_smallorder_money, buy_midorder_count, buy_midorder_money, buy_bigorder_count, 
                 buy_bigorder_money, buy_superorder_count, buy_superorder_money, sell_amount, sell_volume, sell_order_count,  
                 sell_unique_order_count, sell_smallorder_count, sell_smallorder_money, sell_midorder_count, sell_midorder_money, 
                 sell_bigorder_count, sell_bigorder_money, sell_superorder_count, sell_superorder_money]
        
        result = pd.concat(rlist, axis = 1)
        result.columns = columns_list
        result[columns_list] = result[columns_list].fillna(0)

        price = price.to_frame().fillna(method = 'ffill')
        price.columns = [stk]

        return [price, result]

def get_hf_index_by_date(cur_date):
    # 处理weight shift，获取股票列表
    last_tdate = int(udt.get_trading_day_offset(cur_date, -1)[0].strftime('%Y%m%d'))
    weight_name = weight_name_dict[index_name]
    index_wt = IO.read_data([last_tdate, cur_date], columns=[weight_name], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    index_wt_shift = pd.DataFrame(index_wt[weight_name].unstack().shift(1).stack(), columns=[weight_name])
    md = IO.read_data([cur_date], columns=['pre_close'])
    
    global md_index_wt, time_df, time_df_index
    
    md_index_wt = index_wt_shift[index_wt_shift[weight_name] > 0].join(md).join(divdata).fillna(0)
    md_index_wt['pre_close_adj'] = md_index_wt['pre_close'] + md_index_wt['CASH_DVD_PER_SH_PRE_TAX']
    md_index_curdate = md_index_wt.loc[pd.to_datetime(str(cur_date))]
    index_data = IO.read_data([cur_date], universe=name_dict[index_name], columns=['pre_close'],dtype=DType.INDEX).reset_index('Ticker', drop=True)

    # 获取当日近月连续 设定时间戳
    time_df = get_time_df(cur_date)
    time_df_index = time_df.set_index('dt').index
    
    stk_list = [[x, cur_date] for x in index_wt_shift[index_wt_shift[weight_name] > 0].index.get_level_values(1).tolist()]

    with Pool(24) as pool:
        stk_result_list = pool.map(get_stk, stk_list)

    cls_df = pd.concat([x[0] for x in stk_result_list], axis = 1)
    # ---提取权重
    index_wgts = md_index_curdate[[weight_name]]
    # # ---提取前收盘价，计算涨跌幅
    pct_chg_df = cls_df.loc[opentime:] / md_index_curdate['pre_close_adj'] - 1
    index_results = pd.DataFrame()
    index_results['acm_pct_chg'] = (pct_chg_df * md_index_curdate[weight_name]).sum(axis=1)  # 指数累计涨跌幅
    index_results['price'] = index_data.loc[pd.to_datetime(str(cur_date)), 'pre_close'] * (1 + index_results['acm_pct_chg'])  # 指数点位
    for c in columns_list:
        index_results[c] = pd.concat([x[1][c] for x in stk_result_list], axis = 1).sum(axis=1)
    index_results = index_results.reset_index()
    index_results['dt'] = pd.to_datetime(index_results['dt'].apply(lambda x: int(cur_date) * 1000000000 + int(x)),format='%Y%m%d%H%M%S%f')
    index_results = index_results.set_index('dt')
    index_results.to_csv(os.path.join(index_savepath, str(cur_date) + '.csv'))

for index_name in ['hs300','zz500']:
    index_savepath = os.path.join('/data/user/015626/data/share/', 'MD','CHINA_INDEX','TICK', index_name.upper())
    if not os.path.exists(index_savepath):
        os.makedirs(index_savepath)
    future_savepath = os.path.join('/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/RECENT_MONTH/',future_name_dict[index_name].replace('.','_'))
    if not os.path.exists(future_savepath):
        os.makedirs(future_savepath)
        
    _,_,cdate_list = check_update_date(20210101,20211117) 
    for cdate in cdate_list:
        print(index_name, cdate)
        get_hf_index_by_date(cdate)