# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 17:41:43 2022

@author: appadmin
"""

sim = False

jyzh_ic = '5160701'
jyzh_if = '5160701'

recent_future_ic = ''
recent_future_if = ''

# 平今接口
pjjk_ic = 'false'
pjjk_if = 'false'
if jyzh_ic == '5160701':
    pjjk_ic = 'false'
if jyzh_if == '5160701':
    pjjk_if = 'false'


#model_list = ['ic_prod_v6', 'ic_short_v1', 'ic_trade_v1', 'if_v6nl']
model_list = ['ic_v7c', 'ic_v7c_orig', 'ic_short_v3c','if_v6nl', 'if_v6nl_orig']
model_date_dict = {#ic_prod_v6':'20220715_ic_ic_prod_v6_fix',
                   'if_v6nl':'20221125_if_if_v6nl',
                   #'ic_trade_v1':'20220513_ic_trade_v1_ic2',
                   #'ic_short_v1':'20221021_ic_ic_short_v2',
                   'if_v6nl_orig': '20221125_if_if_v6nl',
                   'ic_v7c': '20221125_ic_ic_v7c',
                   'ic_v7c_orig': '20221125_ic_ic_v7c',
                   'ic_short_v3c': '20221125_ic_ic_short_v3c'
                   }

# 初始资金
cszj_dict = {'ic_prod_v6': 0,
             'if_v6nl':32,
             'if_v6nl_orig':13,
             'ic_trade_v1':0,
             'ic_short_v1':0,
             'ic_v7c': 15,
             'ic_v7c_orig': 15,
             'ic_short_v3c': 15            
            }


rank_dict = {'ic_prod_v6': [4800, 2400],
                   'if_v6nl':[4800, 2400],
                   'if_v6nl_orig':[4800, 2400],
                   'ic_trade_v1':[4800, 2400],
                   'ic_short_v1':[1200, 1200],
                   'ic_v7c':[4800, 2400],
                   'ic_v7c_orig':[4800, 2400],
                   'ic_short_v3c':[4800, 2400]
                    }

lstm_dict = {'ic_prod_v6': 30,
                   'if_v6nl':10,
                   'if_v6nl_orig':10,
                   'ic_trade_v1':30,
                   'ic_short_v1':30,
                   'ic_v7c': 10,
                   'ic_v7c_orig': 10,
                   'ic_short_v3c': 10
                
                    }
                
vol_dict = {'ic_prod_v6': 30,
                   'if_v6nl':30,
                   'if_v6nl_orig':0,
                   'ic_trade_v1':30,
                   'ic_short_v1':0,
                   'ic_v7c': 30,
                   'ic_v7c_orig': 0,
                   'ic_short_v3c': 0 
                    }

pos_dict = {}
pos_dict['ic_prod_v6'] =[[0.0, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007],
                          [0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 100.0],
                          [0, 0, 0, 3.33, 6.66, 10],
                          [0, 3.33, 6.66, 10, 10, 10]]

pos_dict['if_v6nl'] = [[0.0, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008],
                              [0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 100],
                              [0, 0, 0, 0, 0, 3.33, 6.66, 10],
                              [0, 3.33, 6.66, 10, 10, 10, 10, 10]]

pos_dict['ic_trade_v1'] =[[0.0, 0.0004, 0.0005, 0.0006, 0.0007],
                          [0.0004, 0.0005, 0.0006, 0.0007, 100.0],
                          [0, 0, 3.33, 6.66, 10],
                          [0, 3.33, 6.66, 10, 10]]

pos_dict['ic_short_v1'] =[[0.0, 0.1, 0.2, 0.8, 0.9],
                              [0.1, 0.2, 0.8, 0.9, 100.0],
                              [0, 0, 0, 5, 10],
                              [0, 5, 10, 10, 10]]

pos_dict['ic_short_v3c'] =[[0.0, 0.1, 0.2, 0.8, 0.9],
                              [0.1, 0.2, 0.8, 0.9, 100.0],
                              [0, 0, 0, 5, 10],
                              [0, 5, 10, 10, 10]]
                            
pos_dict['if_v6nl_orig'] =[[0.0, 0.3, 0.4, 0.8, 0.9],
                              [0.3, 0.4, 0.8, 0.9, 100.0],
                              [0, 0, 0, 5, 10],
                              [0, 5, 10, 10, 10]]

pos_dict['ic_v7c_orig'] =[[0.0, 0.3, 0.4, 0.8, 0.9],
                              [0.3, 0.4, 0.8, 0.9, 100.0],
                              [0, 0, 0, 5, 10],
                              [0, 5, 10, 10, 10]]
                            
pos_dict['ic_v7c'] = [[0.0, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008],
                              [0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 100],
                              [0, 0, 0, 0, 0, 3.33, 6.66, 10],
                              [0, 3.33, 6.66, 10, 10, 10, 10, 10]]
                            


for item in pos_dict.keys():
    assert(len(pos_dict[item][0]) == len(pos_dict[item][1]) == len(pos_dict[item][2]) == len(pos_dict[item][3])), 'FUCK!'

    
model_date_ic = []
vol_window_ic = []
cszj_ic = []
rank_list1_ic = [] 
rank_list2_ic = []

model_date_if = []
vol_window_if = []
cszj_if = []
rank_list1_if = [] 
rank_list2_if = []

pos_ic0 = []
pos_ic1 = []
pos_ic2 = []
pos_ic3 = []
pos_ic4 = []

pos_if0 = []
pos_if1 = []
pos_if2 = []
pos_if3 = []
pos_if4 = []

lstm_ic = []
lstm_if = []

count_ic = 0
count_if = 0
for model in (model_list):
    if 'ic_' in model:
        count_ic = count_ic + 1
        model_date_ic.append(model_date_dict[model])
        vol_window_ic.append(vol_dict[model])
        lstm_ic.append(lstm_dict[model])
        cszj_ic.append(cszj_dict[model])
        rank_list1_ic.append(rank_dict[model][0])
        rank_list2_ic.append(rank_dict[model][1])
        pos_ic0 = pos_ic0 + (pos_dict[model][0])
        pos_ic1 = pos_ic1 + (pos_dict[model][1])
        pos_ic2 = pos_ic2 + (pos_dict[model][2])
        pos_ic3 = pos_ic3 + (pos_dict[model][3])
        pos_ic4_temp = [count_ic] *len(pos_dict[model][0])
        pos_ic4 = pos_ic4 + pos_ic4_temp
    elif 'if_' in model:
        count_if = count_if + 1
        model_date_if.append(model_date_dict[model])
        vol_window_if.append(vol_dict[model])
        lstm_if.append(lstm_dict[model])
        cszj_if.append(cszj_dict[model])
        rank_list1_if.append(rank_dict[model][0])
        rank_list2_if.append(rank_dict[model][1])
        pos_if0 = pos_if0 + (pos_dict[model][0])
        pos_if1 = pos_if1 + (pos_dict[model][1])
        pos_if2 = pos_if2 + (pos_dict[model][2])
        pos_if3 = pos_if3 + (pos_dict[model][3])
        pos_if4_temp = [count_if] *len(pos_dict[model][0])
        pos_if4 = pos_if4 + pos_if4_temp
        
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

_,date,_ = check_update_date()

next_tday = udt.get_trading_day_offset(str(date),1)[0].strftime('%Y%m%d')

savepath = os.path.join('/data/user/016700/Data/para/', 'Mobius_' + next_tday)
if not os.path.exists(savepath):
    os.makedirs(savepath)

iw = IO.read_data([date], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
zz500_list = iw[iw.index_weight_zz500 > 0].index.get_level_values(1).tolist()
hs300_list = iw[iw.index_weight_hs300 > 0].index.get_level_values(1).tolist()

def retrieve_suspension_helper(release_resource = True):
        data = job_wrapper(query_last_mdcontant, OnRecvMDConstant, postprocess_mdconstant, release_resource = release_resource)
        data = data[data.TradingPhaseCode == '8']
        return data.index.tolist()

#suspension_list = retrieve_suspension_helper()

#zz800_list = zz500_list + hs300_list
#zz800_suspension_list = list(set(zz800_list) & set(suspension_list))
#if len(zz800_suspension_list) == 0:
#    suspension_info = '    '
#else:
#    suspension_info = str(zz800_suspension_list)[1:-1].replace("'","").replace(' ','')
suspension_info = '    '
s = FactorData()

WIND_AShareEODPrices = s.get_factor_value('WIND_AShareEODPrices',factors = ['S_INFO_WINDCODE','S_DQ_CLOSE','S_DQ_ADJFACTOR'], trade_dt=str(date))
WIND_AShareEODPrices = WIND_AShareEODPrices.sort_values(by = ['S_INFO_WINDCODE'])
WIND_AShareEODPrices.columns = ['股票代码','T-1日收盘价','T-1日adjFactor']
WIND_AShareEODPrices['T-1日收盘价'] = WIND_AShareEODPrices['T-1日收盘价'].fillna(1.0)
WIND_AShareEODPrices['T日查到的前收盘价'] = WIND_AShareEODPrices['T-1日收盘价']
WIND_AShareEODPrices = WIND_AShareEODPrices[['股票代码','T-1日收盘价','T日查到的前收盘价','T-1日adjFactor']]
zz500 = WIND_AShareEODPrices[WIND_AShareEODPrices['股票代码'].isin(zz500_list)]
hs300 = WIND_AShareEODPrices[WIND_AShareEODPrices['股票代码'].isin(hs300_list)]

'''
FUCK CDR, FUCK CSI

fuck = '689009.SH'
from xquant.marketdata import MarketData
mdp = MarketData()
tick = mdp.get_data_by_date("Stock", fuck, str(date), ['1','2','3', '4','5'])
def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
tick['dt'] = tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
tick = tick.set_index('dt')
preclose_spec = float(tick['LastPx'].iloc[-1])
temp_listdf = pd.DataFrame([fuck, preclose_spec, preclose_spec, 1], index = zz500.columns).T
zz500 = pd.concat([zz500, temp_listdf])
'''

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
fu = future_univ.copy()
#    # 给出次日universe，默认和前一日一样
#    nextfuture_univ = future_univ[future_univ['交易日'] == pd.to_datetime(str(date))]
#    nextfuture_univ['交易日'] = pd.to_datetime(str(next_tday))
#    future_univ = future_univ.append(nextfuture_univ)
#    future_univ = future_univ.sort_values(by = '交易日')

future_univ['交易日'] = future_univ['交易日'].apply(lambda x:x.strftime('%Y-%m-%d'))
future_univ = future_univ.replace('NaN','na')
future_univ = future_univ.fillna(value = 'na')

future_univ.to_csv(os.path.join(savepath, 'future_univ.csv'), index = False, encoding='gbk')

for contract_cat in ['IC.CFE', 'IF.CFE']:
    trade_nextday = fu.set_index(['交易日', '期货品种']).xs(contract_cat.replace('.CFE', ''), level = 1)['近月合约代码'].loc[str(next_tday)]
    trade_lastday = fu.set_index(['交易日', '期货品种']).xs(contract_cat.replace('.CFE', ''), level = 1)['近月合约代码'].loc[str(date)]
    if trade_nextday != trade_lastday:
        lm = link.LinkMessage()
        lm.sendMessage('即将换月，交易品种%s'%trade_nextday)
        del lm
    
    if 'IC' in contract_cat:
        pos0 = pos_ic0
        pos1 = pos_ic1
        pos2 = pos_ic2
        pos3 = pos_ic3
        pos4 = pos_ic4
        
        model_date = model_date_ic
        vol_window = vol_window_ic
        cszj = cszj_ic
        rank_list1 = rank_list1_ic
        rank_list2 = rank_list2_ic
        lstm = lstm_ic
        jyzh = jyzh_ic
        recent_future = recent_future_ic
        
    else:
        pos0 = pos_if0
        pos1 = pos_if1
        pos2 = pos_if2
        pos3 = pos_if3
        pos4 = pos_if4
        
        model_date = model_date_if
        vol_window = vol_window_if
        cszj = cszj_if
        rank_list1 = rank_list1_if
        rank_list2 = rank_list2_if
        lstm = lstm_if
        jyzh = jyzh_if
        recent_future = recent_future_if
    
    
    sc = []
    hsig = []
    for i, mi in enumerate(model_date):

        history_menu_title = str(next_tday) + '_' + str(mi)
        sc.append('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/%s/' % (str(mi)))
        hsig.append(('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historySignal' % (history_menu_title)))
    
        
    if recent_future.endswith( '.CF'):
        pass
    else:
        recent_future = IO.read_data([next_tday], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
        recent_future = recent_future.xs(contract_cat, level = 1)['contract_00'].tolist()[0][:-1]
    print(recent_future)
    def get_trade_starttime(date, next_tday):
        if (datetime.datetime.strptime(str(next_tday),'%Y%m%d') - datetime.datetime.strptime(str(date),'%Y%m%d')).days > 3:
            return '10:00:00'
        else:
            return '09:39:00'
            
    trade_starttime = get_trade_starttime(date, next_tday)
    
    
    di = {}
    try:

        dfff = pd.read_excel('/data/user/011477/order/tradingReport/tradingStat_%s.xlsx'%date, sheet_name='Tri_51606')#.set_index('委托方向')
        l = dfff['组合名称']
        l = [item for item in l if (('mobius' in item.lower()) & (jyzh in item)) | (('hongye' in item.lower()) & (jyzh in item))][0]
        positions = dfff[dfff['组合名称'] == l]['期货持仓'].iloc[0]
        dic_temp = json.loads(positions.replace("'", '"'))

        di['short'] = dic_temp[recent_future[:-3] + '空仓']

        di['long'] = dic_temp[recent_future[:-3] + '多仓']
        
        if sim == True:
            di['long'] = 0
            di['short'] = 0
        else:
            if di['short'] == di['long']:
                pass
            #else:
                #position_min = np.min([di['short'], di['long']])
                #di['long'] = position_min
                #di['short'] = position_min
    except:
        di['long'] = 0
        di['short'] = 0
        
    if 'IC' in contract_cat.upper():
        factor_init = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_v3.0.4.json'
        xdjg = 1
        hycs = 200
        pjjk = pjjk_ic
        trail = ''
    else:
        factor_init = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_IF_v3.0.4.json'
        xdjg = 0.8
        hycs = 300
        pjjk = pjjk_if
        trail = '_if'
    # 交易账户为5160603时 证券账户为  00060160
    paradict = {'合约代码': recent_future,
                '交易日期': int(next_tday),
                '行情分钟数据目录': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/mobius_data_for_prod/minuteData/%s/' % str(next_tday),
                
                '历史因子文件目录': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/' % (next_tday + '_all' + trail),
                '因子配置文件': factor_init,
                '是否记录因子值': 'true',
                '静态信息查询失败时是否使用本地文件': 'true',
                '是否校验历史数据': 'false',
                '中证800停牌列表': suspension_info,
                '开始处理分钟聚合数据时间': '09:30:00',
                '买入交易账户': jyzh,
                '卖出交易账户': jyzh,
                '买入证券账户': '00000004',
                '卖出证券账户': '00000004',
                '合约乘数': hycs,
                #'初始资金（千万元）': 40,
                '止损比例': 0.005,
                '下单价格滑点': xdjg,
                '下单间隔': 2,
                '订单存续时间(秒)': 5,

                '交易开始时间': trade_starttime,
                '开仓截止时间': '14:29:00',
                '平仓开始时间': '14:45:00',
                '平仓结束时间': '14:50:00',
                '废单次数上限': 800,
                '过去1分钟最大下单次数': 120,
                '当日成交总量': 1500,
                '是否调用平今仓接口': pjjk,
                '当日撤单次数上限': 400,
                '多组模型是否并行预测': 'true'
                #'波动率时间窗口': 30
               }
    
    paradict2 = {'合约代码': [recent_future],
                 '平仓优先级': [1],
                 '多头持仓':[di['long']],
                 '空头持仓': [di['short']]
        
                }
    
    paradict3 = {'信号编号': list(range(1, len(sc)+1)),
                 '对应模型目录': sc,
                 '历史信号文件目录':hsig,
                 '初始资金（千万元）': cszj,
                 '波动率时间窗口': vol_window,
                 'Rank周期1':  rank_list1,
                 'Rank周期2':  rank_list2,
                 'LSTM模型输入因子步长':lstm
                }
    
    
    signal_to_pos = {'信号左边界': pos0,
                     '信号右边界': pos1,
                     '仓位左边界': pos2,
                     '仓位右边界': pos3,
                     '所属信号编号': pos4}

                        
    signal_to_pos = pd.DataFrame(signal_to_pos)   
    InitialBasicParam = pd.DataFrame(paradict, index = ['num'])
    InitialPos = pd.DataFrame(paradict2)
    Sig_init = pd.DataFrame(paradict3)
    if sim == True:
        writer = pd.ExcelWriter(os.path.join(savepath, 'MobiusStrategy_%s_sim.xlsx' % (contract_cat[:-4] + '_' +str(next_tday))))
    else:
        writer = pd.ExcelWriter(os.path.join(savepath, 'MobiusStrategy_%s.xlsx' % (contract_cat[:-4] + '_' +str(next_tday))))
    InitialBasicParam.to_excel(writer, 'InitialBasicParam', index=False)
    InitialPos.to_excel(writer, '期初持仓列表', index=False)
    signal_to_pos.to_excel(writer, '信号到仓位配置参数', index=False)
    Sig_init.to_excel(writer, '信号模型配置列表', index=False)
    hs300.to_excel(writer, '沪深300成分股收盘价信息', index=False)
    zz500.to_excel(writer, '中证500成分股收盘价信息', index=False)
    future_univ.to_excel(writer, '最近30个交易日主力近月合约信息', index=False)
    writer.save()