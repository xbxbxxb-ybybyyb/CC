# @Time : 2020/10/13 15:10
# @Author : Zhichen Lu
# @File : trading_record_analysis.py
import pandas as pd
import numpy as np
from multiprocessing import Pool,Manager
from dataApi.stockList import clean_stock_list
from StrongStockModel.System.LoadLabel.LabelDataSet import LabelDataSet

origin_record = pd.read_pickle('/data/user/015664/AFuckingTrigger/record_XGB_40_revised.pkl')
record = Manager().dict()
buy_trigger_times = Manager().dict()
sell_trigger_times = Manager().dict()
for key in origin_record:
    record[key] = origin_record[key]



# def get_trigger_point(k):
#     trigger_point = record[k][record[k]['flag'].eq('B')].index.tolist()
#     buy_list = [list(x) for x in trigger_point]
#     trigger_point = record[k][record[k]['flag'].eq('S')].index.tolist()
#     sell_list = [list(x) for x in trigger_point]
#     print(k)
#     return buy_list,sell_list

def get_daily_first_trigger_point(k):
    buy_list = record[k][record[k]['flag'].eq('B')].reset_index()[['date','time']].groupby('date').min().reset_index().values.tolist()
    sell_list = record[k][record[k]['flag'].eq('S')].reset_index()[['date','time']].groupby('date').min().reset_index().values.tolist()
    print(k)
    return buy_list,sell_list

def get_daily_trigger_times(k):
    buy_trigger_times[k] = record[k][record[k]['flag'].eq('B')].reset_index()[['date','time']].groupby('date').size()
    sell_trigger_times[k] = record[k][record[k]['flag'].eq('S')].reset_index()[['date','time']].groupby('date').size()
    print(k)

pool = Pool(20)
res_list = pool.map(get_daily_trigger_times,list(origin_record.keys()))
pool.close()
pool.join()

buy_trigger_info = pd.DataFrame(buy_trigger_times._getvalue())
sell_trigger_info = pd.DataFrame(sell_trigger_times._getvalue())
pd.to_pickle([buy_trigger_info,sell_trigger_info],'/data/user/015664/AFuckingTrigger/buy_sell_info.pkl')


buy_trigger_info,sell_trigger_info = pd.read_pickle('/data/user/015664/AFuckingTrigger/buy_sell_info.pkl')
buy_trigger_info,sell_trigger_info = buy_trigger_info.sort_index(axis=1),sell_trigger_info.sort_index(axis=1)

trigger_day_count = buy_trigger_info.count()

stock_pool = clean_stock_list(stock_list='COMMON', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, start_date=buy_trigger_info.index[0], end_date=buy_trigger_info.index[-1])

stock_pool_1000 = clean_stock_list(stock_list='ZZ1000', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, start_date=buy_trigger_info.index[0], end_date=buy_trigger_info.index[-1])

stock_pool_800 = stock_pool*(~stock_pool_1000.reindex())>0

stat_800 = (buy_trigger_info>0) * stock_pool_800.reindex(buy_trigger_info.index,axis=0).reindex(buy_trigger_info.columns,axis=1)
pct_800 = stat_800.sum(axis=1)/(buy_trigger_info>0).sum(axis=1)

stat_1000 = (buy_trigger_info>0) * stock_pool_1000.reindex(buy_trigger_info.index,axis=0).reindex(buy_trigger_info.columns,axis=1)
pct_1000 = stat_1000.sum(axis=1)/(buy_trigger_info>0).sum(axis=1)

stat_1800 = (buy_trigger_info>0) * stock_pool.reindex(buy_trigger_info.index,axis=0).reindex(buy_trigger_info.columns,axis=1)
pct_1800 = stat_1800.sum(axis=1)/(buy_trigger_info>0).sum(axis=1)

check = pd.DataFrame({800:pct_800,1000:pct_1000,1800:pct_1800})
check[800] = check[1800] - check[1000]


# data = pd.DataFrame({'buy':buy_trigger_info.mean(axis=1),'sell':sell_trigger_info.mean(axis=1)})
# data['year'] = [x//10000 for x in data.index]
# stat = data.groupby('year').mean().T
# stat['all'] = data.mean()
# with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/XGB每日触发均值.xlsx') as writer:
#     data.to_excel(writer,sheet_name='daily')
#     stat.T.to_excel(writer,sheet_name='yearly')
# writer.close()

"""
buy_list,sell_list = [],[]
for b_list,s_list in res_list:
    buy_list = buy_list + b_list
    sell_list = sell_list + s_list

buy_info = pd.DataFrame(buy_list,columns=['date','time'])
buy_info['year'] = buy_info['date']//10000
sell_info = pd.DataFrame(sell_list,columns=['date','time'])
sell_info['year'] = sell_info['date']//10000

buy_point_count = buy_info.groupby(['time','year']).size().to_frame().reset_index().pivot_table(index='time',columns='year',values=0)
buy_point_count['all'] = buy_info.groupby('time').size()
sell_point_count = sell_info.groupby(['time','year']).size().to_frame().reset_index().pivot_table(index='time',columns='year',values=0)
sell_point_count['all'] = sell_info.groupby('time').size()

with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/XGB第一次买卖分布_revised.xlsx') as writer:
    buy_point_count.to_excel(writer,sheet_name='买入次数')
    (buy_point_count/buy_point_count.sum()).to_excel(writer, sheet_name='买入次数比例')
    sell_point_count.to_excel(writer,sheet_name='卖出次数')
    (sell_point_count / sell_point_count.sum()).to_excel(writer, sheet_name='卖出次数比例')
writer.close()
"""
