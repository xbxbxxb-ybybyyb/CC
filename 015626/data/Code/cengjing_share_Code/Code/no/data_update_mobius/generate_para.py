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

model_date = 20211119

#_,_,cdate_list = check_update_date()
#for date in cdate_list:
def retrieve_suspension_helper(release_resource = True):
    data = job_wrapper(query_last_mdcontant, OnRecvMDConstant, postprocess_mdconstant, release_resource = release_resource)
    data = data[data.TradingPhaseCode == '8']
    return data.index.tolist()

suspension_list = retrieve_suspension_helper() 
    
_,date,_ = check_update_date()
next_tday = udt.get_trading_day_offset(str(date),1)[0].strftime('%Y%m%d')
savepath = os.path.join('/data/user/015626/data/share/para/', 'Mobius_' + next_tday)
if not os.path.exists(savepath):
    os.makedirs(savepath)

iw = IO.read_data([date], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
zz500_list = iw[iw.index_weight_zz500 > 0].index.get_level_values(1).tolist()
hs300_list = iw[iw.index_weight_hs300 > 0].index.get_level_values(1).tolist()

zz800_list = zz500_list + hs300_list
zz800_suspension_list = list(set(zz800_list) & set(suspension_list))
if len(zz800_suspension_list) == 0:
    suspension_info = '    '
else:
    suspension_info = str(zz800_suspension_list)[1:-1].replace("'","").replace(' ','')

s = FactorData()

WIND_AShareEODPrices = s.get_factor_value('WIND_AShareEODPrices',factors = ['S_INFO_WINDCODE','S_DQ_CLOSE','S_DQ_ADJFACTOR'], trade_dt=str(date))
WIND_AShareEODPrices = WIND_AShareEODPrices.sort_values(by = ['S_INFO_WINDCODE'])
WIND_AShareEODPrices.columns = ['股票代码','T-1日收盘价','T-1日adjFactor']
WIND_AShareEODPrices['T-1日收盘价'] = WIND_AShareEODPrices['T-1日收盘价'].fillna(1.0)
WIND_AShareEODPrices['T日查到的前收盘价'] = WIND_AShareEODPrices['T-1日收盘价']
WIND_AShareEODPrices = WIND_AShareEODPrices[['股票代码','T-1日收盘价','T日查到的前收盘价','T-1日adjFactor']]
zz500 = WIND_AShareEODPrices[WIND_AShareEODPrices['股票代码'].isin(zz500_list)]
hs300 = WIND_AShareEODPrices[WIND_AShareEODPrices['股票代码'].isin(hs300_list)]

zz500.to_csv(os.path.join(savepath, 'zz500.csv'), index = False, encoding='gbk')
hs300.to_csv(os.path.join(savepath, 'hs300.csv'), index = False, encoding='gbk')

fore30day = udt.get_trading_day_offset(str(date), -30)[0].strftime('%Y%m%d')
future_univ = IO.read_data([fore30day, next_tday],columns=['contract_main','contract_00'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
future_univ = future_univ[['contract_main','contract_00']].reset_index()
future_univ['Ticker'] = future_univ.Ticker.apply(lambda x:x.split('.')[0])
future_univ.columns = ['交易日','期货品种','主力合约代码','近月合约代码']
future_univ['主力合约代码'] = future_univ['主力合约代码'].apply(lambda x:x[:-1])
future_univ['近月合约代码'] = future_univ['近月合约代码'].apply(lambda x:x[:-1])
future_univ.columns = ['交易日','期货品种','主力合约代码','近月合约代码']
    
#    # 给出次日universe，默认和前一日一样
#    nextfuture_univ = future_univ[future_univ['交易日'] == pd.to_datetime(str(date))]
#    nextfuture_univ['交易日'] = pd.to_datetime(str(next_tday))
#    future_univ = future_univ.append(nextfuture_univ)
#    future_univ = future_univ.sort_values(by = '交易日')

future_univ['交易日'] = future_univ['交易日'].apply(lambda x:x.strftime('%Y-%m-%d'))
future_univ = future_univ.replace('NaN','na')
future_univ = future_univ.fillna(value = 'na')

future_univ.to_csv(os.path.join(savepath, 'future_univ.csv'), index = False, encoding='gbk')

recent_future = IO.read_data([next_tday], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
recent_future = recent_future.xs('IC.CFE', level = 1)['contract_00'].tolist()[0][:-1]

def get_trade_starttime(date, next_tday):
    if (datetime.datetime.strptime(str(next_tday),'%Y%m%d') - datetime.datetime.strptime(str(date),'%Y%m%d')).days > 3:
        return '10:00:00'
    else:
        return '09:39:00'
        
trade_starttime = get_trade_starttime(date, next_tday)
# 交易账户为5160603时 证券账户为  00060160
paradict = {'合约代码': recent_future,
            '交易日期': int(next_tday),
            '行情分钟数据目录': '/data/group/800445/mobius_data_for_prod/minuteData/%s/' % str(next_tday),
            '模型目录': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/%s/' % str(model_date),
            '历史数据目录': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/' % str(next_tday),
            '是否记录因子值': 'true',
            '静态信息查询失败时是否使用本地文件': 'true',
            '是否校验历史数据': 'false',
            '中证800停牌列表': suspension_info,
            '开始处理分钟聚合数据时间': '09:30:00',
            '买入交易账户': '5160604',
            '卖出交易账户': '5160604',
            '买入证券账户': '00000004',
            '卖出证券账户': '00000004',
            '合约乘数': 200,
            '初始资金（千万元）': 4.5,
            '止损比例': 0.005,
            '下单价格滑点': 1.2,
            '下单间隔': 2,
            '订单存续时间(秒)': 5,
            '期初多头持仓': 0,
            '期初空头持仓': 0,
            '交易开始时间': trade_starttime,
            '开仓截止时间': '14:30:00',
            '平仓开始时间': '14:45:00',
            '平仓结束时间': '14:50:00',
            '废单次数上限': 200,
            '过去1分钟最大下单次数': 120,
            '当日成交总量': 1000,
            '是否调用平今仓接口': 'true',
            '当日撤单次数上限': 350}

signal_to_pos = {'信号左边界': [0.0, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008],
                 '信号右边界': [0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 100.0],
                 '仓位左边界': [0, 0, 0, 3.33, 6.66, 10],
                 '仓位右边界': [0, 3.33, 6.66, 10, 10, 10]} 
                    
signal_to_pos = pd.DataFrame(signal_to_pos)   
        
InitialBasicParam = pd.DataFrame(paradict, index = ['num'])

writer = pd.ExcelWriter(os.path.join(savepath, 'MobiusStrategy_IC_%s.xlsx' % str(next_tday)))
InitialBasicParam.to_excel(writer, 'InitialBasicParam', index=False)
signal_to_pos.to_excel(writer, '信号到仓位配置参数', index=False)
hs300.to_excel(writer, '沪深300成分股收盘价信息', index=False)
zz500.to_excel(writer, '中证500成分股收盘价信息', index=False)
future_univ.to_excel(writer, '最近30个交易日主力近月合约信息', index=False)
writer.save()