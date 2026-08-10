from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as dt
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData

s = FactorData()
from xquant.marketdata import MarketData
from multiprocessing import Pool
import datetime


start_date = 20190101
end_date = 20200603
index_name = 'zz500'

pre_start_date = dt.get_trading_day_offset(start_date, -1)[0]
name_dict = {'hs300': '000300.SH', 'zz500': '000905.SH', 'sz50': '000016.SH'}
weight_name_dict = {'hs300':'index_weight_hs300','zz500':'index_weight_zz500','sz50':'index_weight_sh50'}
future_name_dict={'hs300':'IF_CFE','zz500':'IC_CFE','sz50':'IH_CFE'}
freq = 3000
rootdir = os.path.join('/data/user/015626/data/share/MD/CHINA_INDEX', 'TICK_3s', index_name.upper())
if not os.path.exists(rootdir):
    os.makedirs(rootdir)
opentime = '092500000'

divdata = IO.read_data([start_date, end_date], alt=os.path.join('/data/group/800080/warehouse/prod', 'DATABASE', 'WIND', 'AShareDividend', 'AShareDividend.h5'))\
    .reset_index()[['Ticker', 'CASH_DVD_PER_SH_PRE_TAX', 'EX_DT']]
divdata['dt'] = pd.to_datetime(divdata['EX_DT'], format="%Y%m%d")
divdata = divdata[['dt', 'Ticker', 'CASH_DVD_PER_SH_PRE_TAX']].dropna().set_index(['dt', 'Ticker'])

tradingdays = dt.get_trading_date_range(pre_start_date, end_date)
md = IO.read_data(tradingdays,dsource=DSource.WIND, columns=['pre_close'])
weight_name = weight_name_dict[index_name]
index_wt = IO.read_data(tradingdays, columns=[weight_name], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
index_wt_shift = pd.DataFrame(index_wt[weight_name].unstack().shift(1).stack(), columns=[weight_name])
md_index_wt = index_wt_shift[index_wt_shift[weight_name] > 0].join(md).join(divdata).fillna(0)
md_index_wt['pre_close_adj'] = md_index_wt['pre_close'] + md_index_wt['CASH_DVD_PER_SH_PRE_TAX']
index_data = IO.read_data(tradingdays, universe=name_dict[index_name], columns=['pre_close'],
                          dtype=DType.INDEX, dsource=DSource.WIND).reset_index('Ticker', drop=True)

def get_results(cur_date):
    stock_start_time = datetime.datetime.now()
    mdp = MarketData()
    cur_date_str = cur_date.strftime('%Y%m%d')
    md_index_curdate = md_index_wt.loc[cur_date]
    print(cur_date_str)
    time_df = pd.DataFrame()
    t1 = pd.Series(
        pd.date_range(start='9:30:00', end='11:30', freq=str(freq) + 'L').strftime('%H%M%S%f')).apply(
        lambda x: x[:-3])
    t2 = pd.Series(
        pd.date_range(start='13:00:00', end='15:00', freq=str(freq) + 'L').strftime('%H%M%S%f')).apply(
        lambda x: x[:-3])
    time_df['MDTime'] = t1.append(t2)
    time_df['index'], time_df['TradePrice'], time_df['TradeAmt'], time_df['flag'] = np.nan, np.nan, np.nan, 1
    cls_df_last = pd.DataFrame(np.nan, index=time_df['MDTime'], columns=md_index_curdate.index.tolist())
    cls_df_buy1 = pd.DataFrame(np.nan, index=time_df['MDTime'], columns=md_index_curdate.index.tolist())
    cls_df_sell1 = pd.DataFrame(np.nan, index=time_df['MDTime'], columns=md_index_curdate.index.tolist())
    amt_df_last = pd.DataFrame(np.nan, index=time_df['MDTime'], columns=md_index_curdate.index.tolist())
    amt_df_buy1 = pd.DataFrame(np.nan, index=time_df['MDTime'], columns=md_index_curdate.index.tolist())
    amt_df_sell1 = pd.DataFrame(np.nan, index=time_df['MDTime'], columns=md_index_curdate.index.tolist())

    data_dict = {}
    susp_list = []
    no_open_list = []
    for i in range(len(md_index_curdate)):
        stk = md_index_curdate.index[i]
        try:
            df = mdp.get_data_by_time_frame('Stock',stk, cur_date_str+ " 092450000", cur_date_str+" 150100000", sort_by_receive_time=True)
        except:
            df = pd.DataFrame(columns = ['MDTime','Buy1Price','Buy1OrderQty','Sell1Price','Sell1OrderQty','LastPx','TotalValueTrade'])
        if len(df) > 0:
            df = df.fillna(0).sort_values(by='MDTime')
            df['Buy1Price'] = df['Buy1Price'].where(df['Buy1Price']>0, df['Sell1Price'])
            df['Sell1Price'] = df['Sell1Price'].where(df['Sell1Price']>0, df['Buy1Price'])
            df['LastPx'] = df['LastPx'].where(df['LastPx']>0, df['Buy1Price'])
            if df['Buy1Price'].iloc[0]==0:
                df['Buy1Price'].iloc[0] == md_index_curdate['pre_close'].iloc[i]
            if df['Sell1Price'].iloc[0]==0:
                df['Sell1Price'].iloc[0] == md_index_curdate['pre_close'].iloc[i]
            if df['LastPx'].iloc[0] == 0:
                df['LastPx'].iloc[0] == md_index_curdate['pre_close'].iloc[i]

            df['Buy1Price']=df['Buy1Price'].replace(0,np.nan).fillna(method='pad')
            df['Sell1Price']=df['Sell1Price'].replace(0,np.nan).fillna(method='pad')
            df['LastPx'] = df['LastPx'].replace(0,np.nan).fillna(method='pad')

        use_df = df[['MDTime','Buy1Price','Buy1OrderQty','Sell1Price','Sell1OrderQty','LastPx','TotalValueTrade']]
        use_df['Buy1Amt'] = (use_df['Buy1Price'] * use_df['Buy1OrderQty'])
        use_df['Sell1Amt'] = (use_df['Sell1Price'] * use_df['Sell1OrderQty'])
        use_df['flag'] = 0
        merge_df = pd.concat([use_df, time_df]).sort_values(['MDTime', 'index']).fillna(method='ffill')

        if len(use_df) == 0:
            results = merge_df[merge_df['flag'] == 1].drop(columns=['flag']).set_index('MDTime')
            cls_df_last[stk] = md_index_curdate['pre_close'].iloc[i]
            amt_df_last[stk] = 0
            cls_df_buy1[stk] = md_index_curdate['pre_close'].iloc[i]
            amt_df_buy1[stk] = 0
            cls_df_sell1[stk] = md_index_curdate['pre_close'].iloc[i]
            amt_df_sell1[stk] = 0
            susp_list.append(stk)
        else:
            merge_df = merge_df.sort_values(['MDTime', 'index']).fillna(method='ffill')
            results = merge_df[merge_df['flag'] == 1].drop(columns=['flag']).set_index('MDTime')
            cls_df_last[stk] = results['LastPx']
            amt_df_last[stk] = results['TotalValueTrade']
            cls_df_buy1[stk] = results['Buy1Price']
            amt_df_buy1[stk] = results['Buy1Amt']
            cls_df_sell1[stk] = results['Sell1Price']
            amt_df_sell1[stk] = results['Sell1Amt']

    index_wgts = md_index_curdate[[weight_name]]
    pct_chg_df_last = cls_df_last.loc[opentime:] / md_index_curdate['pre_close_adj'] - 1
    pct_chg_df_buy1 = cls_df_buy1.loc[opentime:] / md_index_curdate['pre_close_adj'] - 1    
    pct_chg_df_sell1 = cls_df_sell1.loc[opentime:] / md_index_curdate['pre_close_adj'] - 1    

    index_results = pd.DataFrame()
    index_results['acm_pct_chg_last'] = (pct_chg_df_last * md_index_curdate[weight_name]).sum(axis=1)
    index_results['acm_pct_chg_buy1'] = (pct_chg_df_buy1 * md_index_curdate[weight_name]).sum(axis=1)
    index_results['acm_pct_chg_sell1'] = (pct_chg_df_sell1 * md_index_curdate[weight_name]).sum(axis=1)
    index_results['LastPx'] = index_data.loc[cur_date, 'pre_close'] * (1 + index_results['acm_pct_chg_last'])
    index_results['Buy1Price'] = index_data.loc[cur_date, 'pre_close'] * (1 + index_results['acm_pct_chg_buy1'])
    index_results['Sell1Price'] = index_data.loc[cur_date, 'pre_close'] * (1 + index_results['acm_pct_chg_sell1'])

    index_results['TotoalValue'] = amt_df_last.sum(axis=1)
    index_results['Buy1Amt'] = amt_df_buy1.sum(axis=1)
    index_results['Sell1Amt'] = amt_df_sell1.sum(axis=1)

    index_results = index_results.reset_index()
    index_results['dt'] = pd.to_datetime(index_results['MDTime'].apply(lambda x: int(cur_date_str) * 1000000000 + int(x)),
                                         format='%Y%m%d%H%M%S%f')
    index_results.set_index('dt')[['LastPx','TotoalValue','Buy1Price','Buy1Amt','Sell1Price','Sell1Amt']].to_csv(os.path.join(rootdir, cur_date_str + '.csv'))
    print(cur_date_str, datetime.datetime.now() - stock_start_time)
    del(mdp)
    
with Pool(processes = 24) as pool:
    pool.map(get_results, tradingdays[1:])