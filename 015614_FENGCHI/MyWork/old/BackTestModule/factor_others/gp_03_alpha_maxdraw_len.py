import pandas as pd
from pandas import DataFrame
import numpy as np
import os
# os.chdir('/data/group/800319/BackTestModule/')
#   alpha1
from config import *
from QuickFactorEvaluationBackTest import FactorBackTest
import time
import sys
sys.path.append('/data/group/800319')
from dataApi.getData import get_minute_1factor,get_daily_1factor
from dataApi.stockList import clean_stock_list

def get_section_rank(x):
    return x.argsort().argsort()

def getidmax(x):
    return len(x) - x.argmax()

# 因子逻辑：
# 反转类指标
# score = maxDraw * maxDrawLen
# maxDraw为开盘以来超额收益率高点至今的回撤
# maxDrawLen开盘以来超额收益率高点至今分钟数

start = 20190101
end = 20191231
trading_day_all = s.tradingday(20160101, 20191231, \
                           frequency='DAY', dayType=None, dateType='TRADINGDAYS')
trading_day_all = list(map(int, trading_day_all))
trading_day = [item for item in  trading_day_all if ((item >= start) & (item <= end)) ]
start, end = trading_day[0],trading_day[-1]

factor_name = 'gp_03_alpha_maxdraw_len'
indexcode = 'ZZ500'
pcnt_high = 0.2
pcnt_low = 0.1
e1 = time.time()


#定义股票池
# stock_pool50 = get_index_comp(start,end,'SH50')
# stock_pool300 = get_index_comp(start,end,'HS300')
stock_pool500 = get_index_comp(start,end,'ZZ500')
# stock_pool1000 = get_index_comp(start,end,'ZZ1000')

# 排序池
stock_pool_all = clean_stock_list(no_ST=True, stock_list= 'COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                 no_limit_up=False, no_limit_down=False,
                 address='/data/group/800319/junkData/daily')
# stock_list must in (ALL, COMMON, HS300, ZZ500, ZZ1000)

# 入选池
stock_pool_in = stock_pool500[start]
stock_pool_in = [item for item in stock_pool_in if item in stock_pool_all.columns]

codeList = list(stock_pool_all.columns)

#日频高开低收
# 不复权价格
close = get_daily_1factor('close', date_list= trading_day, code_list=codeList, type='stock')
# 前复权价格，计算区间涨跌幅
close_adj = get_daily_1factor('close_badj', date_list= trading_day_all, code_list=codeList, type='stock')
pctb = close_adj.pct_change(60).loc[close.index].fillna(0)
del close_adj
# pe_ttm
pe = get_daily_1factor('pe_ttm', date_list= trading_day, code_list=codeList, type='stock')

# 可买入股票前60日涨跌幅在全市场分位数处于 10% - 80%
pctb_up = pctb.quantile(0.8,axis =1)
pctb_down = pctb.quantile(0.1,axis =1)

bool_pctb_up = pctb.sub(pctb_up, axis=0) < 0
bool_pctb_down = pctb.sub(pctb_down, axis=0) > 0

# 可买入股票  0 < pe < 300
bool_pe_up = pe < 300
bool_pe_down = pe > 0

bool_clean = stock_pool_all.loc[close.index] & bool_pctb_up & bool_pctb_down & bool_pe_up & bool_pe_down

#定义因子信号
factor_df_list = []
for datei in trading_day:
    begi = datei * 10000 + 930
    endi = datei * 10000 + 1500
    bool_cleani = bool_clean.loc[datei]
    # 不复权分钟收盘价
    temp_minutest_data = get_minute_1factor('close', start_datetime = begi, end_datetime = endi,
                                    code_list = codeList)
    # # 前复权分钟收盘价
    # temp_minutest_data_adj = get_minute_1factor('close_badj', start_datetime = begi, end_datetime = endi,
    #                                 code_list = codeList[:2])
    # # 成交额
    # temp_minutest_amt = get_minute_1factor('amt', start_datetime=begi, end_datetime=endi,
    #                                         code_list=codeList[:2])

    temp_minutest_data_index = get_minute_1factor('close', start_datetime = begi, end_datetime = endi,type='bench' )
    temp_minutest_data_index = temp_minutest_data_index[indexcode].ffill()

    profit = temp_minutest_data/ temp_minutest_data.iloc[0]
    profit_index = temp_minutest_data_index / temp_minutest_data_index.iloc[0]
    alphai = profit .sub(profit_index,axis = 0)
    alphai.fillna(0.0,inplace = True)

    # 开盘以来超额收益率高点至今的回撤
    max_draw = alphai - alphai.expanding(min_periods = 1).max()
    max_draw_len = alphai.expanding(min_periods=1).apply(getidmax)
    score = max_draw *  max_draw_len

    highBand = score.quantile(pcnt_high,axis =1)
    lowBand = score.quantile(pcnt_low,axis =1)
    # 1买入
    factor_df = score .sub(lowBand ,axis = 0)
    factor_df.where(factor_df < 0, np.nan, inplace=True)
    factor_df.where(factor_df.isna(), 1, inplace=True)
    # 对买入股票池进行筛选
    stk_clean = bool_cleani[~bool_cleani].index.intersection(factor_df.columns)
    factor_df[stk_clean] = 0
    # -1卖出
    factor_df2 = score.sub(highBand ,axis = 0)
    factor_df2.where(factor_df2 > 0, 0.0, inplace=True)
    factor_df2.where(factor_df2 <=0, -1,inplace = True )

    factor_df.fillna(factor_df2,inplace = True)
    factor_df.fillna(0,inplace = True)

    factor_df.iloc[:30,:] = 0
    factor_df.iloc[-3:, :] = 0
    factor_df_list.append(factor_df)

factor_df = pd.concat(factor_df_list,axis = 0 )
factor_df = factor_df[stock_pool_in]
del factor_df2
factor_df = factor_df.astype(int)
factor_df.index = [x*10000 + y for x,y in  factor_df.index]
# factor_df.to_hdf('/data/group/800319/factorScripts/alpha01.h5', 'alpha01')
# factor_df.to_excel('/data/group/800319/factorScripts/alpha01.xlsx')
# del temp_minutest_data
print(time.time() - e1)
e1 = time.time()

#定义因子回测对象
factor_test = FactorBackTest(factor_df)
print(time.time()-e1)
# del factor_df
#并行回测
factor_test.evaluation(6)
factor_test.result_output(factor_name, '/data/user/006693/')
factor_test.result_output(factor_name, '/data/group/800319/factorScripts/')
res = factor_test.evaluation_result.T
resDay = factor_test.evaluation_result_daily
netValue = factor_test.net_value
trading_records = factor_test.trading_record




