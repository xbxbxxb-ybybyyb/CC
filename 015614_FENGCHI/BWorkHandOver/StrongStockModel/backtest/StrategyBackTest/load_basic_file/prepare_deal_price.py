# @Time : 2020/11/13 9:54
# @Author : Zhichen Lu
# @File : prepare_deal_price.py
import sys
sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/015614/BWorkHandOver')
sys.path.append('/data/user/015614/BWorkHandOver/ensemblemonitor-strategy-python')
sys.path.append('/data/user/015614/BWorkHandOver/StrongStockModel')
# from dataApi.getData import get_minute_1factor,get_minute_pickle
from dataApi.getData import get_minute_pickle
from dataApi.tradeDate import get_date_range
from StrongStockModel.conf.path_config import deal_price_path,root_path
import pandas as pd
import numpy as np
from dataApi.usefulTools import frame2arr
import datetime,traceback
from xquant.xqutils.helper import link
from dataApi.sendInfo import send_message
lm = link.LinkMessage()

lm.sendMessage('成交价更新开始')
from dataApi.tradeDate import get_recent_trade_date
today = get_recent_trade_date()
try:
    stock_pool = pd.read_pickle(root_path + 'stock_pool_without_limit_up_down.pkl')
    if stock_pool.index[-1]!=today:#int(datetime.date.today().strftime('%Y%m%d')):
       lm.sendMessage('成交量更新-股票池截止日期不是当日')
       raise Exception('成交量更新-股票池截止日期不是当日')
    # close = get_minute_1factor('close', start_datetime= 20160104 * 10000 + 925, end_datetime=stock_pool.index[-1] * 10000 + 1500,
    #                                    code_list=stock_pool.columns.tolist())
    # close = get_minute_pickle('close',date_list=get_date_range(20160104,stock_pool.index[-1]),code_list=stock_pool.columns.tolist())
    # vol = get_minute_1factor('vol', start_datetime= 20160104 * 10000 + 925, end_datetime=stock_pool.index[-1] * 10000 + 1500,
    #                                    code_list=stock_pool.columns.tolist()).fillna(0)

    close = get_minute_pickle('close', date_list=get_date_range(20160104, stock_pool.index[-1]), code_list=stock_pool.columns.tolist())
    vol = get_minute_pickle('volume', date_list=get_date_range(20160104, stock_pool.index[-1]), code_list=stock_pool.columns.tolist()).fillna(0)

    vwap = {}
    for window in [5,30]:
        temp_vwap = ((close*vol).rolling(window).sum()/vol.rolling(window).sum()).shift(-window)
        temp_vwap[temp_vwap.eq(np.inf)] = np.nan
        temp_vwap[temp_vwap.eq(-np.inf)] = np.nan
        vwap[window] = temp_vwap
        # pd.to_pickle(vwap[window].loc[20160104:20181228], deal_price_path + 'deal_price_vwap_%dmin_20160104_20181228.pkl' % window)
#        pd.to_pickle(vwap[window].loc[20190102:], deal_price_path + 'deal_price_vwap_%dmin_OutSample.pkl' % window)
        pd.to_pickle(vwap[window], deal_price_path + 'deal_price_vwap_%dmin_FullSample.pkl' % window)
        print(window,'done')
    lm.sendMessage(f'{today}成交价更新完成---------------------')
    send_message(['015664'], f'{today}成交价更新完成---------------------')

except:
    lm.sendMessage(f'{today}成交价更新失败！！！！！！！！！！')
    send_message(['015664'], f'{today}成交价更新失败！！！！！！！！！！')
    print(traceback.format_exc())

