import datetime
import os
import numpy as np
import pandas as pd
import shutil
import json
import time
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from xquant.factordata import FactorData
s = FactorData()

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


money_per_stock = 2500000
model_version = '20230630'
threshold = 0.15
daily_max_num = 50
daily_min_num = 3
blacklist = list(pd.read_csv('/data/user/000072/LYM_STOCKS/blacklist/blacklist.csv', header = None)[0].values)
blacklist_str = ''
for i in blacklist:
    blacklist_str += i + ','
blacklist_str = blacklist_str[:-1]


today = s.tradingday(datetime.datetime.today().strftime('%Y%m%d'), (datetime.datetime.today() + datetime.timedelta(days = 60)).strftime('%Y%m%d'))[1]
#today= '20230417'
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

daily_universe = data[data.filter_subnew & \
                      data.filter_SHSZ & \
                      data.filter_4 & \
                      (data.filter_1 | data.filter_2 | data.filter_3)]

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


params_dir = '/data/user/000072/LYM_STOCKS/arrow_sim/params/'
os.makedirs(params_dir + today)

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
    arrow_portfolio_sell.to_excel(params_dir + today + '/arrow_portfolio_sell_' + today + '.xlsx', index = False)


arrow_portfolio_buy = round(money_per_stock / data.loc[pd.Timestamp(yesterday)].reindex(stocklist.index.get_level_values(level = 1)).S_DQ_CLOSE, -2).to_frame().reset_index()
arrow_portfolio_buy = pd.DataFrame({'证券代码':arrow_portfolio_buy.Ticker, 
                                '买入交易账户':['5160803'] * len(arrow_portfolio_buy), 
                                '卖出交易账户':['5160803'] * len(arrow_portfolio_buy), 
                                '买入证券数量': 2 * arrow_portfolio_buy.S_DQ_CLOSE.astype('int'),
                                '卖出证券数量':[0] * len(arrow_portfolio_buy)})
arrow_portfolio_buy.to_excel(params_dir + today + '/arrow_portfolio_buy_' + today + '.xlsx', index = False)


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
    #     "交易账户": "5161205",
    #     "上海证券账户": "D890272174",
    #     "深圳证券账户": "0899014413",
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
        "交易参数":trading_params_sell
    }

    out_file = open(params_dir + today + '/sell_' + today + '.json', 'w')
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
                            "交易结束时间": "93500",
                            "停止下单时间": "93500",
                            "交易算法": "tvol",
                            "跟单比例(%)": "10",
                            "下单间隔(s)": "1",
                            "撤单时间(s)": "1",
                            "补单价格": "99",
                            "下单价格": "1",
                            "首单比例(%)": "20",
                            "首单价格": "0"
                            })

buy_list = {
    "交易日期": pd.Timestamp(today).strftime('%Y-%m-%d'),
#     "交易账户": "5161205",
#     "上海证券账户": "D890272174",
#     "深圳证券账户": "0899014413",
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
    '交易参数':trading_params_buy
}

out_file = open(params_dir + today + '/buy_' + today + '.json', 'w')
json.dump(buy_list, out_file, indent = 4, ensure_ascii = False)
out_file.close()


shutil.copytree(params_dir + today, '/data/user/000072/share/arrow_sim_params/' + today)