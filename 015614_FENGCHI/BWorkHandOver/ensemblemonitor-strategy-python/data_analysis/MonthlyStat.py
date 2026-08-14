# @Time : 2022/5/5 15:23
# @Author : Zhichen Lu
# @File : MonthlyStat.py

import pandas as pd
import numpy as np
import os
from dataApi.getData import trans_windcode2int,trans_int2windcode
from dataApi.tradeDate import get_date_range,get_pre_trade_date

non_fix_path = '/data/group/800319/strategy_local_path3/'
# non_fix_930_path = f'{non_fix_path}FolderFor930/'
# non_fix_in_path = f'{non_fix_path}daily_input/'
# non_fix_output_path = f'{non_fix_path}daily_output/'

morning_path = '/data/user/011477/order/O32/morning/'
afternoon_path = '/data/user/011477/order/O32/afternoon/'
trading_record_path = '/data/user/011477/order/O32/514/trade/'

def format_df(df, port_id, index=None):
    df['组合编号'] = df['组合编号'].apply(lambda x: str(x)[:len(port_id)])
    df = df[df['组合编号'].eq(port_id)].set_index('证券代码')
    if '交易市场' in df.columns:
        df = df[df['交易市场'].isin(['深交所A', '上交所A'])]
    df.index = df.index.astype(int).map(trans_int2windcode)
    return df

def get_info(date, port_id):
    local_config_path = non_fix_path
    morning_portfolio = pd.read_excel(f'{morning_path}综合信息查询_组合证券{date}_516.xls')
    if os.path.exists(f'{afternoon_path}综合信息查询_组合证券_{date}.xls'):
        print('read afternoot from 011477')
        afternoon_portfolio = pd.read_excel(f'{afternoon_path}综合信息查询_组合证券_{date}.xls')
    elif os.path.exists(f'{local_config_path}restrict_list/{date}/综合信息查询_组合证券.xls'):
        afternoon_portfolio = pd.read_excel(f'{local_config_path}restrict_list/{date}/综合信息查询_组合证券.xls')
        print('read afternoon file from 800319')
    else:
        raise Exception('No Afternoon file exist')
    if os.path.exists(f'{trading_record_path}综合信息查询_委托流水_{date}_EM.xls'):
        trading_record = pd.read_excel(f'{trading_record_path}综合信息查询_委托流水_{date}_EM.xls')
    else:
        trading_record = pd.read_excel(f'{local_config_path}restrict_list/{date}/综合信息查询_委托流水.xls')

    morning_portfolio = format_df(morning_portfolio, port_id)
    afternoon_portfolio = format_df(afternoon_portfolio, port_id)
    trading_record = format_df(trading_record, port_id)
    return morning_portfolio, afternoon_portfolio, trading_record

date_list = get_date_range(20220501,20220531)

trading_num = {}
trade_amt = {}
holding_cap = {}
# date = date_list[1]
from tqdm import tqdm
for date in tqdm(date_list):
    _,af,tr = get_info(date,port_id='201001')
    trading_num[date] = len(set(af[~af['净买金额'].eq(0)].index))
    trade_amt[date] = tr.groupby('委托方向').sum()['成交金额']
    holding_cap[date] = af['市值'].sum()

res = pd.DataFrame(trade_amt).T.fillna(0)
res['收盘持仓市值'] = pd.Series(holding_cap)
res['交易股票只数'] = pd.Series(trading_num)
res['交易金额'] = res['买入'] + res['卖出']
res['收盘持仓市值'] = res['收盘持仓市值']#.shift(1)
m_res = res.loc[date_list[1]:].mean()
# m_res['换手率'] = m_res['交易金额']/res[res['收盘持仓市值']>100000].mean()['收盘持仓市值']/2
m_res['换手率'] = m_res['交易金额']/m_res['收盘持仓市值']/2

# (res['买入'].replace(0,np.nan).sum()+res['卖出'].replace(0,np.nan).sum())/res['收盘持仓市值'].replace(0,np.nan).sum()/2

# m_res['收盘持仓市值']

# res[res['收盘持仓市值']>100000].mean()['收盘持仓市值']

from dataApi.sendInfo import send_message

send_message(['015664'],f'{dict(m_res)}')
