import sys
sys.path.insert(1,'/data/user/015626/JupyterNotebooks/utils/')
import datetime
import os
import numpy as np
import pandas as pd
import shutil
import json
import time
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from xquant.factordata import FactorData
s = FactorData()


# In[2]:


_,end_date,_ = check_update_date()
next_tdate = udt.get_trading_day_offset(end_date, 1)[0].strftime('%Y%m%d')

para_path = f'/data/group/800466/trade/Arrow/para/Arrow_{next_tdate}_sim'
path_in_sim = f'/data/cppParam/ArrowCppStrategy/Arrow_{next_tdate}_sim'

zone = '#304301'


# In[3]:


# eod = IO.read_data([end_date], alt = '/data/group/800080/warehouse/test/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5')
# eod_list = eod[eod['S_DQ_CLOSE'] == eod['S_DQ_LIMIT']].index.get_level_values(1).tolist()

# eod = eod.reset_index(level = 0, drop = True)
# eod['num'] = (30000 / eod['S_DQ_CLOSE']).astype('int')
# eod['num'] = 100 * eod['num']

# plist = eod['num'].loc[eod_list].tolist()

# eod_list = [x for x in zip(eod_list,plist)]

# temppp = eod['num'].loc[eod_list].reset_index()

# temppp.columns = ['证券代码', '当前数量']


# In[4]:


def get_md_params_json():
    arrow_udp_path = os.path.join(para_path, 'md_params', 'arrow_udp')
    arrow_udp_front_path = os.path.join(para_path, 'md_params', 'arrow_udp-front')
    os.makedirs(arrow_udp_path, exist_ok=True)
    os.makedirs(arrow_udp_front_path, exist_ok=True)

    md_params_dict = {
        "ip": "168.62.5.47",
        "port": 18088,
        "user": "USERATSQUANTUDPSIM05",
        "password": "ge.u_+EYcsW9qP",
        "backup": [
            {
                "ip": "168.62.5.48",
                "port": 18088
            }
        ],
        "interface_ip": "100.69.9.65"
    }

    output_file = open(os.path.join(arrow_udp_path, 'arrow-udp-config-168.62.1.62.json'), 'w')
    json.dump(md_params_dict, output_file, indent = 4, ensure_ascii = False)
    output_file.close()

    udp_front_dict = {'path':os.path.join(path_in_sim,'md_params', 'arrow_udp', 'arrow-udp-config-168.62.1.62.json')}
    output_file = open(os.path.join(arrow_udp_front_path, f'Arrow_udp{zone}.json'), 'w')
    json.dump(udp_front_dict, output_file, indent = 4, ensure_ascii = False)
    output_file.close()

def get_strategy_params(next_tdate):
    arrow_strategy_path = os.path.join(para_path, 'strategy_params', 'arrow_strategy')
    arrow_strategy_front_path = os.path.join(para_path, 'strategy_params', 'arrow_strategy-front')
    os.makedirs(arrow_strategy_path, exist_ok=True)
    os.makedirs(arrow_strategy_front_path, exist_ok=True)

    udp_front_dict = {'path':os.path.join(path_in_sim,'strategy_params', 'arrow_strategy', f'buy_{next_tdate}.json')}
    output_file = open(os.path.join(arrow_strategy_front_path, f'arrow_buy{zone}.json'), 'w')
    json.dump(udp_front_dict, output_file, indent = 4, ensure_ascii = False)
    output_file.close()

    udp_front_dict = {'path':os.path.join(path_in_sim,'strategy_params', 'arrow_strategy', f'sell_{next_tdate}.json')}
    output_file = open(os.path.join(arrow_strategy_front_path, f'arrow_sell{zone}.json'), 'w')
    json.dump(udp_front_dict, output_file, indent = 4, ensure_ascii = False)
    output_file.close()
get_md_params_json()
get_strategy_params(next_tdate)


# In[5]:




def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(cache=None)
def retrieve_st_stocks(date):
    date = IO.str_date_parser(date)
    if retrieve_st_stocks.cache is None:
        cache = IO.read_data(columns=['REMOVE_DT', 'ENTRY_DT'], dtable=DTable.AShareST).reset_index('dt', drop=True)
        cache['REMOVE_DT'] = pd.to_datetime(cache['REMOVE_DT'], format='%Y%m%d')
        cache['ENTRY_DT'] = pd.to_datetime(cache['ENTRY_DT'], format='%Y%m%d')
        cache['REMOVE_DT'].loc[cache['REMOVE_DT'].isnull()] = pd.Timestamp.max
        retrieve_st_stocks.cache = cache
    else:
        cache = retrieve_st_stocks.cache
    return cache[(cache['ENTRY_DT'] <= date) & (cache['REMOVE_DT'] > date)].index.unique().tolist()


def retrieve_st_stocks_range(start_date, end_date):
    collector = list()
    for trading_day in tdt.get_trading_date_range(start_date, end_date):
        st_stocks = retrieve_st_stocks(trading_day)
        collector.append(pd.Series(True, index=pd.MultiIndex.from_product([[trading_day], st_stocks], names=['dt', 'Ticker'])))
    return pd.concat(collector)


money_per_stock = 6000000
model_version = '20230825'
threshold = 0.15
daily_max_num = 50
daily_min_num = 0
blacklist = list(pd.read_csv('/data/user/000072/LYM_STOCKS/blacklist/blacklist.csv', header = None)[0].values)
blacklist_str = ''
for i in blacklist:
    blacklist_str += i + ','
blacklist_str = blacklist_str[:-1]


today = s.tradingday(datetime.datetime.today().strftime('%Y%m%d'), (datetime.datetime.today() + datetime.timedelta(days = 60)).strftime('%Y%m%d'))[1]
# today= '20230925'
yesterday = s.tradingday((pd.Timestamp(today) - datetime.timedelta(days = 60)).strftime('%Y%m%d'), today)[-2]
# today = '20230109'
# yesterday = '20230106'

##############池子##############
dates = s.tradingday((pd.Timestamp(today) - datetime.timedelta(days = 60)).strftime('%Y%m%d'), today)

date_bgn = dates[0]
date_end = dates[-2]

data = IO.read_data([date_bgn, date_end], alt = '/data/group/800080/warehouse/test/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5')
filt = IO.read_data([date_bgn, date_end], dtype=DType.STOCK, ftype=FType.UNIV, dsource=DSource.OPTM)
data = data.join(filt)
data.Listing_date = data.Listing_date.groupby('Ticker').fillna(method = 'ffill').fillna(0).astype('int')

data = data[data.Listing_date > 0]

data['listing_days'] = [x.days for x in np.array([x[0] for x in data.index]) - np.array([pd.Timestamp(str(x)) for x in data.Listing_date.values])]
data['filter_subnew'] = ((data.listing_days > 1) & (data.S_DQ_LOW < data.S_DQ_LIMIT)).groupby('Ticker').expanding().sum().reset_index(level = 0, drop = True) > 1
data['filter_SHSZ'] = data.reset_index()['Ticker'].str.contains('SH|SZ').values


data['filter_1'] = (data.S_DQ_HIGH == data.S_DQ_LIMIT) & (data.S_DQ_CLOSE < data.S_DQ_LIMIT)

data['filter_2'] = (data.S_DQ_HIGH > 1.04 * data.S_DQ_OPEN) & (data.S_DQ_CLOSE < data.S_DQ_OPEN)

data['filter_3'] = (data.groupby('Ticker').shift(1).S_DQ_CLOSE == data.groupby('Ticker').shift(1).S_DQ_LIMIT) & (data.S_DQ_CLOSE < data.S_DQ_LIMIT)

data['filter_4'] = data.S_DQ_CLOSE > data.S_DQ_STOPPING

daily_universe = data[data.filter_subnew &                       data.filter_SHSZ &                       data.filter_4 &                       (data.filter_1 | data.filter_2 | data.filter_3)]

##############次新股加入blacklist##############
#daily_universe = daily_universe.loc[pd.Timestamp(date_end)].reset_index()['Ticker']
daily_universe = daily_universe.loc[pd.Timestamp(date_end)]
subnew_list = daily_universe[daily_universe.listing_days<90].reset_index()['Ticker'].to_list()
for i in subnew_list:
    blacklist_str += ',' + i
##############次新股加入blacklist##############

daily_universe = list(daily_universe.reset_index()['Ticker'])
st_stocks = retrieve_st_stocks(date_end)
stocklist = [x for x in daily_universe if x not in st_stocks]
#stocklist = list(s.stock_filter(list(daily_universe), date_end, 'STSPEND').stock)
#stocklist = [x for x in stocklist if x not in blacklist]

stocklist = pd.DataFrame({'dt':[pd.Timestamp(today)] * len(stocklist), 'Ticker':stocklist}).set_index(['dt', 'Ticker'])
    
#stocklist.to_pickle(root_path + today + '/universe/stock_universe.pkl')

###fake universe###
#stocklist = pd.read_pickle('/data/user/000072/share/for_lym/arrow/stock_universe.pkl')
#stocklist = stocklist[stocklist.dt == pd.Timestamp(today)]
#stocklist = stocklist.set_index(['dt', 'Ticker'])
################################


params_dir = f'/data/group/800466/trade/Arrow/para/Arrow_{today}_sim/strategy_params/arrow_strategy/'

while True:
    if (os.path.exists('/data/user/011477/order/O32/afternoon/组合证券' + yesterday + '.xlsx')) and (os.path.exists('/data/user/011477/order/Trade/委托流水' + yesterday + '_arrow.xlsx')):
        break
    else:
        print (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S'), 'no position file yet')
        time.sleep(60)

position = pd.read_excel('/data/user/011477/order/O32/afternoon/组合证券' + yesterday + '.xlsx', dtype = {'证券代码':str})
position = position.loc[position.组合编号 == 2100][['证券代码', '当前数量', '交易市场']]
position.loc[position.交易市场 == '上海', '证券代码'] += '.SH'
position.loc[position.交易市场 == '深圳', '证券代码'] += '.SZ'
position = position[position.当前数量 > 0]

if len(position) > 0:
    arrow_portfolio_sell = pd.DataFrame({'证券代码':position.证券代码, 
                                    '买入交易账户':['5160803'] * len(position), 
                                    '卖出交易账户':['5160803'] * len(position), 
                                    '买入证券数量':[0] * len(position),
                                    '卖出证券数量':position.当前数量.astype('int')})
    arrow_portfolio_sell.to_excel(params_dir + '/arrow_portfolio_sell_' + today + '.xlsx', index = False)


arrow_portfolio_buy = round(money_per_stock / data.loc[pd.Timestamp(yesterday)].reindex(stocklist.index.get_level_values(level = 1)).S_DQ_CLOSE, -2).to_frame().reset_index()
arrow_portfolio_buy = pd.DataFrame({'证券代码':arrow_portfolio_buy.Ticker, 
                                '买入交易账户':['5160803'] * len(arrow_portfolio_buy), 
                                '卖出交易账户':['5160803'] * len(arrow_portfolio_buy), 
                                '买入证券数量': 2 * arrow_portfolio_buy.S_DQ_CLOSE.astype('int'),
                                '卖出证券数量':[0] * len(arrow_portfolio_buy)})
arrow_portfolio_buy.to_excel(params_dir + '/arrow_portfolio_buy_' + today + '.xlsx', index = False)


if len(position) > 0:
    txn = pd.read_excel('/data/user/011477/order/Trade/委托流水' + yesterday + '_arrow.xlsx', dtype = {'证券代码':str}).iloc[:-1][['证券代码', '委托方向', '成交金额', '成交数量']]
    txn.loc[txn.证券代码.str.startswith('6'), '证券代码'] += '.SH'
    txn.loc[txn.证券代码.str.startswith('3') | txn.证券代码.str.startswith('0'), '证券代码'] += '.SZ'

    txn_summary_buy = txn.loc[txn.委托方向 == '买入'].groupby('证券代码').sum().reset_index()
    txn_summary_buy = txn_summary_buy.loc[txn_summary_buy.成交数量 > 0]
    #txn_summary_sell = txn.loc[txn.委托方向 == '卖出'].groupby('证券代码').sum()
    #txn_summary_buy['成交均价'] = txn_summary_buy.成交金额 / txn_summary_buy.累计成交数量
    #txn_summary_buy['成交均价'] = txn_summary_buy.成交金额 / txn_summary_buy.累计成交数量

    trading_params_sell = []
    for i in txn_summary_buy.values:
        trading_params_sell.append({
                                "股票代码": i[0],
                                "买卖方向": "S",
                                "交易数量": str(i[2]),
                                "买入金额": "0",
                                "交易开始时间": "133000",
                                "交易结束时间": "140000",
                                "停止下单时间": "145600",
                                "交易算法": "twap",
                                "跟单比例(%)": "0",
                                "下单间隔(s)": "30",
                                "撤单时间(s)": "30",
                                "补单价格": "1",
                                "下单价格": "1",
                                "首单比例(%)": "20",
                                "首单价格": "0"
                                })


    position = position.set_index('证券代码')
    txn_summary_buy = txn_summary_buy.set_index('证券代码')
    sell_AM = (position.当前数量 - txn_summary_buy.reindex(position.index).fillna(0).成交数量).astype('int').rename('qty').to_frame()
    sell_AM = sell_AM.loc[sell_AM.qty > 0].reset_index()
    if len(sell_AM) > 0:
        for i in sell_AM.values:
            trading_params_sell.append({
                                    "股票代码": i[0],
                                    "买卖方向": "S",
                                    "交易数量": str(i[1]),
                                    "买入金额": "0",
                                    "交易开始时间": "93000",
                                    "交易结束时间": "93500",
                                    "停止下单时间": "145600",
                                    "交易算法": "twap",
                                    "跟单比例(%)": "0",
                                    "下单间隔(s)": "5",
                                    "撤单时间(s)": "10",
                                    "补单价格": "1",
                                    "下单价格": "1",
                                    "首单比例(%)": "20",
                                    "首单价格": "0"

                                    }) 
    sell_list = {
        "交易日期": pd.Timestamp(today).strftime('%Y-%m-%d'),
        "数据文件存放目录": "/home/appadmin/EQuant/localdata",
        "Python代码目录": "/home/appadmin/ATS-Quant-sim/strategy/arrow-python",
        "业务数据存放目录": "/data/group/800466/trade/Arrow/trade_files/data_files/" + today,
        "模型存放目录": "/data/group/800466/trade/Arrow/trade_files/model/model_" + model_version,
        "触发计算时间": "09:26:30",
        "Python解释器": "/home/appadmin/anaconda3/bin/python3",
        "跳过Python": "true",
        "决策结果文件": "score.csv",
        "mock测试": "true",
        "预测阈值": str(threshold),
        "最大买入股票数量": str(daily_max_num),
        "最小买入股票数量": str(daily_min_num),
        "买入交易黑名单":blacklist_str,
        "卖出交易黑名单":blacklist_str,
        "每根Tick最大下单单数": "4",
        "是否开板卖出": "true",
        "开始监控时间": "93000",
        "结束监控时间": "145500",
        "初始封单金额(万)": "1000",
        "基础封单金额": "0.99",
        "触发比例": "0.3",
        "触发金额(万)": "1000",
        "卖出委托价格(%)": "1",
        "卖出委托时间(秒)": "100",
        "快照band名称": "tick_udp",
        "全息盘口band列表": "sz_market_data_l2p_2011,sz_market_data_l2p_2012,sz_market_data_l2p_2013,sz_market_data_l2p_2014,sh_market_data_l2p_1,sh_market_data_l2p_2,sh_market_data_l2p_3,sh_market_data_l2p_4,sh_market_data_l2p_5,sh_market_data_l2p_6",        
        "交易参数":trading_params_sell
    }

    out_file = open(params_dir + '/sell_' + today + '.json', 'w')
    json.dump(sell_list, out_file, indent = 4, ensure_ascii = False)
    out_file.close()



trading_params_buy = []
for s in arrow_portfolio_buy.证券代码.values:
    trading_params_buy.append({
                            "股票代码": s,
                            "买卖方向": "B",
                            "交易数量": "0",
                            "买入金额": str(money_per_stock),
                            "交易开始时间": "93000",
                            "交易结束时间": "94000",
                            "停止下单时间": "94000",
                            "交易算法": "indicator_v",
                            "跟单比例(%)": "10",
                            "下单间隔(s)": "1",
                            "撤单时间(s)": "1",
                            "补单价格": "99",
                            "下单价格": "-1",
                            "下单价格delta": "0.01",
                            "首单比例(%)": "20",
                            "首单价格": "1",
                            "首单下单价格delta": "-0.01"
                            })

buy_list = {
    "交易日期": pd.Timestamp(today).strftime('%Y-%m-%d'),
    "数据文件存放目录": "/home/appadmin/EQuant/localdata",
    "Python代码目录": "/home/appadmin/ATS-Quant-sim/strategy/arrow-python",
    "业务数据存放目录": "/data/group/800466/trade/Arrow/trade_files/data_files/" + today,
    "模型存放目录": "/data/group/800466/trade/Arrow/trade_files/model/model_" + model_version,
    "触发计算时间": "09:26:30",
    "Python解释器": "/home/appadmin/anaconda3/bin/python3",
    "跳过Python": "false",
    "决策结果文件": "score.csv",
    "mock测试": "false",
    "预测阈值": str(threshold),
    "最大买入股票数量": str(daily_max_num),
    "最小买入股票数量": str(daily_min_num),
    "买入交易黑名单":blacklist_str,
    "卖出交易黑名单":blacklist_str,
    "每根Tick最大下单单数": "4",
    "逐笔band列表": "sz_market_data_udp_2011,sz_market_data_udp_2012,sz_market_data_udp_2013,sz_market_data_udp_2014,sh_market_data_udp_1,sh_market_data_udp_2,sh_market_data_udp_3,sh_market_data_udp_4,sh_market_data_udp_5,sh_market_data_udp_6",
    "快照band名称": "tick_udp",
    "全息盘口band列表": "sz_market_data_l2p_2011,sz_market_data_l2p_2012,sz_market_data_l2p_2013,sz_market_data_l2p_2014,sh_market_data_l2p_1,sh_market_data_l2p_2,sh_market_data_l2p_3,sh_market_data_l2p_4,sh_market_data_l2p_5,sh_market_data_l2p_6",
    "indicator阈值": "0",
    "v阈值": "0.004",
    '交易参数':trading_params_buy
}

out_file = open(params_dir  + '/buy_' + today + '.json', 'w')
json.dump(buy_list, out_file, indent = 4, ensure_ascii = False)
out_file.close()


# In[6]:


buy_list = pd.read_excel(f'{params_dir}arrow_portfolio_buy_{next_tdate}.xlsx')
buy_list = buy_list['证券代码'].tolist()
if os.path.exists(f'{params_dir}arrow_portfolio_sell_{next_tdate}.xlsx'):
    sell_list = pd.read_excel(f'{params_dir}arrow_portfolio_sell_{next_tdate}.xlsx')
    sell_list = sell_list['证券代码'].tolist()
else:
    sell_list = []

l2p_stk_list = sorted(list(set(buy_list + sell_list)))

def get_txn_summary_buy(end_date):
    txn = pd.read_excel('/data/user/011477/order/Trade/委托流水' + str(end_date) + '_arrow.xlsx', dtype = {'证券代码':str}).iloc[:-1][['证券代码', '委托方向', '成交金额', '成交数量']]
    txn.loc[txn.证券代码.str.startswith('6'), '证券代码'] += '.SH'
    txn.loc[txn.证券代码.str.startswith('3') | txn.证券代码.str.startswith('0'), '证券代码'] += '.SZ'
    txn_summary_buy = txn.loc[txn.委托方向 == '买入'].groupby('证券代码').sum().reset_index()
    txn_summary_buy = txn_summary_buy.loc[txn_summary_buy.成交数量 > 0]
    return txn_summary_buy

def get_l2p_params_json(end_date):
    channel_dict = {'sh':[i for i in range(1,7)],'sz':[i for i in range(2011,2015)]}
#     stk_need_sell = ','.join(get_txn_summary_buy(end_date)['证券代码'].tolist())
    stk_need_sell = ','.join([x.split('.')[0] for x in l2p_stk_list])
    arrow_l2p_path = os.path.join(para_path, 'l2p_params', 'arrow_l2p')
    arrow_l2p_front_path = os.path.join(para_path, 'l2p_params', 'arrow_l2p-front')
    os.makedirs(arrow_l2p_path, exist_ok=True)
    os.makedirs(arrow_l2p_front_path, exist_ok=True)
    fake_stk_list = ['600266.SH','600322.SH','603073.SH','603139.SH','603172.SH','603667.SH','301218.SZ','301349.SZ','301380.SZ','301382.SZ']
    fake_df = pd.DataFrame({'证券代码':fake_stk_list, 
                                        '买入交易账户':['5160803'] * len(fake_stk_list), 
                                        '卖出交易账户':['5160803'] * len(fake_stk_list), 
                                        '买入证券数量':[0] * len(fake_stk_list),
                                        '卖出证券数量':[0] * len(fake_stk_list)})
    fake_df.to_excel(os.path.join(para_path, 'l2p_params', 'arrow_portfolio.xlsx'), index = False)

    i = 0
    for k,v in channel_dict.items():
        for channel_num in v:
            l2p_dict = {
              "market": k,
              "source": 2,
              "channel": str(channel_num),
              "tick_type": 1,
              "stock_set": stk_need_sell,
              "registration": 1,
              "match": 0
            }
            output_file = open(os.path.join(arrow_l2p_path, f'{k}_{channel_num}.json'), 'w')
            json.dump(l2p_dict, output_file, indent = 4, ensure_ascii = False)
            output_file.close()

            l2p_front_dict = {'path':os.path.join(path_in_sim,'l2p_params', 'arrow_l2p',f'{k}_{channel_num}.json')}
            output_file = open(os.path.join(arrow_l2p_front_path, f'{fake_stk_list[i]}{zone}.json'), 'w')
            i += 1
            json.dump(l2p_front_dict, output_file, indent = 4, ensure_ascii = False)
            output_file.close()



get_l2p_params_json(end_date)

