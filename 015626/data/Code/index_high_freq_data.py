import sys
sys.path.insert(4,'/data/user/012398/working_code/prod_zhangf')
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as dt
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData

s = FactorData()
from xquant.marketdata import MarketData
from taskpath import *
tp = TaskPath()
mdp = MarketData()

divdata = IO.read_data(alt=os.path.join(tp.prod_data_path, 'DATABASE', 'WIND', 'AShareDividend', 'AShareDividend.h5'))\
    .reset_index()[['Ticker', 'CASH_DVD_PER_SH_PRE_TAX', 'EX_DT']]
divdata['dt'] = pd.to_datetime(divdata['EX_DT'], format="%Y%m%d")
divdata = divdata[['dt', 'Ticker', 'CASH_DVD_PER_SH_PRE_TAX']].dropna().set_index(['dt', 'Ticker'])

start_date = 20200220
end_date = 20200301
pre_start_date = dt.get_trading_day_offset(start_date, -1)[0]
freq = 500

index_name = 'zz500'
name_dict = {'hs300': '000300.SH', 'zz500': '000905.SH', 'sz50': '000016.SH'}
weight_name_dict = {'hs300':'index_weight_hs300','zz500':'index_weight_zz500','sz50':'index_weight_sh50'}
future_name_dict={'hs300':'IF_CFE','zz500':'IC_CFE','sz50':'IH_CFE'}

rootdir = os.path.join(tp.A, 'data', 'MD','CHINA_INDEX','TICK', index_name.upper())
if not os.path.exists(rootdir):
    os.makedirs(rootdir)
opentime = '092600000'

tradingdays = dt.get_trading_date_range(pre_start_date, end_date)
md = IO.read_data(tradingdays, columns=['pre_close'])
weight_name = weight_name_dict[index_name]
index_wt = IO.read_data(tradingdays, columns=[weight_name], ftype=FType.INDEXWEIGHT, dsource=DSource.CSI)
index_wt_shift = pd.DataFrame(index_wt[weight_name].unstack().shift(1).stack(), columns=[weight_name])
md_index_wt = index_wt_shift[index_wt_shift[weight_name] > 0].join(md).join(divdata).fillna(0)
md_index_wt['pre_close_adj'] = md_index_wt['pre_close'] + md_index_wt['CASH_DVD_PER_SH_PRE_TAX']
index_data = IO.read_data(tradingdays, universe=name_dict[index_name], columns=['pre_close'],
                          dtype=DType.INDEX).reset_index('Ticker', drop=True)
for t in range(1, len(tradingdays)):
    # 提取成分股列表
    cur_date = tradingdays[t]
    cur_date_str = cur_date.strftime('%Y%m%d')
    md_index_curdate = md_index_wt.loc[cur_date]
    print(cur_date_str)
    # 设定时间戳
    futures_data = pd.read_csv(os.path.join('/data/user/015626/data/share/future/MAIN',future_name_dict[index_name], 
    	                       cur_date_str + '.csv'))
    futures_data['MDTime'] = pd.to_datetime(futures_data['dt']).apply(lambda x: x.strftime('%H%M%S%f'))
    drift = futures_data['MDTime'].iloc[2][6]  # 1表示从100ms开始
    time_df = pd.DataFrame()
    t1 = pd.Series(
        pd.date_range(start='9:25:00.' + drift, end='11:31', freq=str(freq) + 'L').strftime('%H%M%S%f')).apply(
        lambda x: x[:-3])
    t2 = pd.Series(
        pd.date_range(start='13:00:00.' + drift, end='15:01', freq=str(freq) + 'L').strftime('%H%M%S%f')).apply(
        lambda x: x[:-3])
    time_df['MDTime'] = t1.append(t2)
    time_df['index'], time_df['TradePrice'], time_df['TradeAmt'], time_df['flag'] = np.nan, np.nan, np.nan, 1
    cls_df = pd.DataFrame(np.nan, index=time_df['MDTime'], columns=md_index_curdate.index.tolist())
    amt_df = pd.DataFrame(np.nan, index=time_df['MDTime'], columns=md_index_curdate.index.tolist())
    # 1.计算个股价格数据：提取成分股transaction数据，每只个股逐笔成交reindex再fillna最后只留下时间戳数据
    data_dict = {}
    susp_list = []
    no_open_list = []
    for i in range(len(md_index_curdate)):
        stk = md_index_curdate.index[i]
        df = mdp.get_data_by_date("Transaction", stk, cur_date_str)
        use_df = df[(df['TradeType'] == 0) & (df['TradePrice'] > 0)].reset_index()[['index', 'MDTime', 'TradePrice', 'TradeQty']]  # 筛选出成交数据
        use_df['TradeAmt'] = (use_df['TradePrice'] * use_df['TradeQty']).cumsum()
        use_df['flag'] = 0
        use_df = use_df.drop(columns=['TradeQty'])
        merge_df = pd.concat([use_df, time_df]).sort_values(['MDTime', 'index']).fillna(method='ffill')

        if len(use_df) == 0:  # 若股票停牌用前收盘价填充
            results = merge_df[merge_df['flag'] == 1].drop(columns=['flag']).set_index('MDTime')
            cls_df[stk] = md_index_curdate['pre_close'].iloc[i]
            amt_df[stk] = 0
            susp_list.append(stk)
        else:
            if use_df['MDTime'].min() >= '093000000':  # 若集合竞价期间无成交记录，用前收盘价代替集合竞价开盘价
                merge_df.loc[merge_df['MDTime'] == opentime, 'TradePrice'] = md_index_curdate['pre_close'].iloc[i]
                merge_df.loc[merge_df['MDTime'] == opentime, 'TradeAmt'] = 0
                no_open_list.append(stk)
            merge_df = merge_df.sort_values(['MDTime', 'index']).fillna(method='ffill')
            results = merge_df[merge_df['flag'] == 1].drop(columns=['flag']).set_index('MDTime')
            cls_df[stk] = results['TradePrice']
            amt_df[stk] = results['TradeAmt']

    # ---提取权重
    index_wgts = md_index_curdate[[weight_name]]
    # ---提取前收盘价，计算涨跌幅
    pct_chg_df = cls_df.loc[opentime:] / md_index_curdate['pre_close_adj'] - 1
    index_results = pd.DataFrame()
    index_results['acm_pct_chg'] = (pct_chg_df * md_index_curdate[weight_name]).sum(axis=1)  # 指数累计涨跌幅
    index_results['price'] = index_data.loc[cur_date, 'pre_close'] * (1 + index_results['acm_pct_chg'])  # 指数点位
    index_results['amt'] = amt_df.sum(axis=1)
    index_results = index_results.reset_index()
    index_results['dt'] = pd.to_datetime(index_results['MDTime'].apply(lambda x: int(cur_date_str) * 1000000000 + int(x)),
                                         format='%Y%m%d%H%M%S%f')
    index_results.set_index('dt')[['price', 'amt']].to_csv(os.path.join(rootdir, cur_date_str + '.csv'))
