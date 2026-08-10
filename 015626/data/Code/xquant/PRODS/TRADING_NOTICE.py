import json,datetime,os,glob
from multiprocessing.pool import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import numpy as np
pd.set_option('max_columns', 200)
import glob
import bottleneck as bk
from xquant.factordata import FactorData
from insight_base import *
from xquant.xqutils.helper import link


user_ids1 = [
    '011477', 
    '012398',
    '016700',
    '022335'
]

'''
_,date,_ = check_update_date()
date = str(date)
next_tday = udt.get_trading_day_offset(str(date),1)[0].strftime('%Y%m%d')

b = date.replace('-', '')

future_traded = []

trading_stats = pd.read_excel('/data/user/011477/order/O32/51606/综合信息查询_成交回报明细_%s_51606.xls'%b)
trading_stats = trading_stats.loc[trading_stats['日期'].isna() == False]
trading_stats['成交时间1'] = pd.to_datetime(trading_stats['成交时间'].apply(lambda x: (b + str(x).replace(':', ''))[:-2]))
#trading_stats = trading_stats[(trading_stats['证券代码'].isin(future_traded))&(trading_stats['组合编号'] == 5160604) & (trading_stats['成交时间1'] >= pd.to_datetime(b + '0939')) & (trading_stats['成交时间1'] <= pd.to_datetime(b + '1450'))].sort_values(by = '成交时间')
trading_stats = trading_stats[(trading_stats['组合编号'].isin([5160701, 5160701.0])) & (trading_stats['成交时间1'] >= pd.to_datetime(b + '0939')) & (trading_stats['成交时间1'] <= pd.to_datetime(b + '1450'))].sort_values(by = '成交时间')
future_traded = set(trading_stats['证券代码'])

dic_temp1 = {}
for item in future_traded:
    if ('IC' in item.upper()) or ('IM' in item.upper()):
        dic_temp1[item] = 200
    if ('IF' in item.upper()) or ('IH' in item.upper()):
        dic_temp1[item] = 300
        
ddata = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_SIF_TICK_TO_DAILY_ALL_CONTRACT.h5').reset_index().set_index('dt')
ddata.Ticker = ddata.Ticker.apply(lambda x: x[:-4])
settle = ddata[ddata.Ticker.isin(future_traded)].loc[date, ['Ticker', 'settle']]

settle['cs'] = settle['Ticker'].apply(lambda x: dic_temp1[x])
settle['price'] = settle['settle'] * settle['cs']

dfff = pd.read_excel('/data/user/011477/order/tradingReport/tradingStat_%s.xlsx'%date, sheet_name='Tri_51606')#.set_index('委托方向')
l = dfff['组合名称']
l = [item for item in l if (('mobius' in item.lower()) & ('5160701' in item)) | (('hongye' in item.lower()) & ('5160701' in item))][0]


positions = dfff[dfff['组合名称'] == l]['期货持仓'].iloc[0]
dic = json.loads(positions.replace("'", '"'))


dic_temp2 = {}
for item in settle['Ticker']:
    
    lp = dic[item + '多仓']
    sp = dic[item + '空仓']
    
    dic_temp2[item] = int(np.min([lp, sp]))

    
settle['pairs'] = settle['Ticker'].apply(lambda x: int(dic_temp2[x]))
single_unit = settle['price'].mean()
max_pairs = np.floor(np.floor(np.sum(settle['price'] * settle['pairs']) / single_unit) + (2.5e8 * (1/0.15) / single_unit))
margin_call = np.floor(max_pairs * 0.7)
capital_needed = np.floor(2e8 - (np.sum(settle['price'] * settle['pairs']) * 0.15)) 
'''

lm = link.LinkMessage(user_ids1)
lm.sendMessage('MOBIUS策略: 请启动两个C++参数，先截面,后UDP')

del lm

#lm = LinkMessage(user_ids2)
#lm.sendMessage('MOBIUS策略: 【51607】弘业账户, 请确保账户有【2.5亿总资金】，谢谢')