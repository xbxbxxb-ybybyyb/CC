# coding: utf-8
# Author：fengchi863
# Date ：2021/8/18 15:45

import datetime

import numpy as np
import pandas as pd
from tqdm import tqdm

from FaaMonitor.Util.DtUtil import DtUtil
from FaaMonitor.dataApi import stockList, getData

if __name__ == '__main__':
    today_date = DtUtil.get_today_date()
    df = pd.read_excel('仿真成交结果.xlsx', sheet_name=f'{today_date}')
    df = df.T.set_index(0).T
    df = df.set_index('股票代码')
    df.index = df.index.map(stockList.trans_windcode2int)

    df['调仓均价'] = np.nan
    df['vwap'] = np.nan
    df['调仓节省'] = np.nan
    code_list = df.index.tolist()
    minute_amount = getData.get_minute_1factor('amt', start_datetime=today_date,
                                               end_datetime=today_date, code_list=code_list)
    minute_vol = getData.get_minute_1factor('vol', start_datetime=today_date,
                                            end_datetime=today_date, code_list=code_list)
    for stk_id in tqdm(code_list):
        try:
            t0_vwap = df.loc[stk_id, '成交金额'] / df.loc[stk_id, '成交量']
        except:
            t0_vwap = 0
        df.loc[stk_id, '调仓均价'] = t0_vwap
        start_time = df.loc[stk_id, '挂单时间']
        start_time = int(datetime.time.strftime(start_time, '%H%M%S'))
        start_time = today_date * 1000000 + start_time
        start_time = datetime.datetime.strptime(str(start_time), '%Y%m%d%H%M%S')
        end_time = start_time + datetime.timedelta(minutes=30)
        start_time = int(start_time.strftime('%H%M'))
        end_time = int(end_time.strftime('%H%M'))

        total_amt = minute_amount.loc[(today_date, start_time):(today_date, end_time), stk_id].sum()
        total_vol = minute_vol.loc[(today_date, start_time):(today_date, end_time), stk_id].sum()
        vwap = total_amt / total_vol
        df.loc[stk_id, 'vwap'] = vwap
        df.loc[stk_id, '调仓节省'] = -(abs(t0_vwap / vwap) - 1)
    print(df)
    pd.Series(df['调仓均价'])
    pd.Series(df['vwap'])
    pd.Series(df['调仓节省'])
