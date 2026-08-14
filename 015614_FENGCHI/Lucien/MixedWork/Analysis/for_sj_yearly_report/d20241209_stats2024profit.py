# coding: utf-8
# Author：fengchi863
# Date ：2024/12/9 13:15

from dataApi.tradeDate import get_date_range
from tqdm import tqdm
import pandas as pd
import numpy as np
from dataApi.sendInfo import send_file

root_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'
strategy = 'Metis'

profit_list = list()
tmp_cumsum = 0
metis_daily_profit = pd.read_excel(root_path + f'Metis成交记录-20241213.xlsx', sheet_name='累计卖出明细')
jupiter_daily_profit = pd.read_excel(root_path + f'jupiter成交记录-20241213.xlsx', sheet_name='累计卖出明细')
europa_daily_profit = pd.read_excel(root_path + f'Europa成交记录-20241213.xlsx', sheet_name='累计卖出明细')
leda_daily_profit = pd.read_excel(root_path + f'Leda成交记录-20241213.xlsx', sheet_name='累计卖出明细')
saturn_daily_profit = pd.read_excel(root_path + f'saturn成交记录-20241213.xlsx', sheet_name='累计卖出明细')

jupiter = jupiter_daily_profit.groupby('买入日期').agg({'卖出部分盈利金额': sum,
                                          '买入金额':sum,
                                          })
jupiter = jupiter.rename({
    '卖出部分盈利金额': 'jupiter卖出部分盈利金额',
    '买入金额': 'jupiter买入金额',
}, axis=1)
metis = metis_daily_profit.groupby('买入日期').agg({'卖出部分盈利金额': sum,
                                          '买入金额':sum,
                                          })
metis = metis.rename({
    '卖出部分盈利金额': 'metis卖出部分盈利金额',
    '买入金额': 'metis买入金额',
}, axis=1)
saturn = saturn_daily_profit.groupby('买入日期').agg({'卖出部分盈利金额': sum,
                                          '买入金额':sum,
                                          })
saturn = saturn.rename({
    '卖出部分盈利金额': 'saturn卖出部分盈利金额',
    '买入金额': 'saturn买入金额',
}, axis=1)
leda = leda_daily_profit.groupby('买入日期').agg({'卖出部分盈利金额': sum,
                                          '买入金额':sum,
                                          })
leda = leda.rename({
    '卖出部分盈利金额': 'leda卖出部分盈利金额',
    '买入金额': 'leda买入金额',
}, axis=1)
europa = europa_daily_profit.groupby('买入日期').agg({'卖出部分盈利金额': sum,
                                          '买入金额':sum,
                                          })
europa = europa.rename({
    '卖出部分盈利金额': 'europa卖出部分盈利金额',
    '买入金额': 'europa买入金额',
}, axis=1)

check = pd.concat([jupiter, europa, metis, leda, saturn], axis=1)

send_file(check)