# @Time : 2021/2/1 13:31
# @Author : Zhichen Lu
# @File : daily_stat.py

import configparser
from online_conf import init_conf_path, daily_out_path, holding_info_path
import pandas as pd
from dataApi.getData import get_minute_1factor
import numpy as np

account_info = {}
for date in [20210105, 20210106, 20210107, 20210108, 20210111, 20210112, 20210113, 20210114, 20210115, 20210118, 20210119, 20210120, 20210121, 20210122, 20210125, 20210126,
             20210127, 20210128]:
    config = configparser.ConfigParser()
    config.read(init_conf_path + '%d.ini' % date)
    account_info[date] = dict(config['account_info'])
account_info = pd.DataFrame(account_info).T.astype(float)
account_info['net'] = account_info['account_value'] / account_info['account_value'].tolist()[0]

holding_vol = {}
cash = {}
for date in [20210105, 20210106, 20210107, 20210108, 20210111, 20210112, 20210113, 20210114, 20210115, 20210118, 20210119, 20210120, 20210121, 20210122, 20210125, 20210126,
             20210127]:
    for bar in [1000, 1030, 1100, 1300, 1330, 1400, 1430]:
        bar_summary = pd.read_pickle(f'{daily_out_path}{date}/{bar}_summary.pkl')
        holding_vol[(date, bar)] = pd.Series(bar_summary['barly_holding_info'].set_index('Symbol')['NetPosition'], name=(date, bar))
        cash[(date, bar)] = bar_summary['bar_inital_cash']

holding_vol = pd.DataFrame(holding_vol).T
involved = holding_vol.sum()
involved = involved[involved > 0]
holding_vol = holding_vol[involved.index]

close = get_minute_1factor('close', start_datetime=202101050925, end_datetime=202101131500, code_list=[int(x[:-3]) for x in holding_vol.columns])
close.columns = holding_vol.columns

holding_mv = close.loc[holding_vol.index] * holding_vol

cash = pd.Series(cash)

mv = pd.DataFrame({'holding': holding_mv.sum(axis=1), 'cash': cash})
mv['total'] = mv.sum(axis=1)
mv['pct'] = mv['total'].pct_change()

online_holding = {}
for date in [20210105, 20210106, 20210107, 20210108, 20210111, 20210112, 20210113, 20210114, 20210115, 20210118, 20210119, 20210120, 20210121, 20210122, 20210125, 20210126,
             20210127]:
    temp_holding = pd.read_pickle(f'{holding_info_path}{date}.pkl')
    online_holding[date] = temp_holding

online_holding = pd.DataFrame(online_holding).T

res_pn, cash_series = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/NoFutureInfoResShift/record/XGB_Light_daily_res_pn_0105_0127.pkl')
offline_mv = res_pn.minor_xs('收盘持仓市值')
offline_mv.columns = [str(x).zfill(6) + '.SZ' if x < 400000 else str(x) + '.SH' for x in offline_mv.columns]

holding_num = pd.DataFrame({'online': (online_holding.drop('cash', axis=1) > 0).sum(axis=1), 'offline': (offline_mv > 0).sum(axis=1)})
holding_num = holding_num[:-1]
holding_num['intersection'] = np.nan
for date in holding_num.index:
    online, offline = online_holding.loc[date], offline_mv.loc[date]
    online, offline = online[online > 0].index.tolist(), offline[offline > 0].index.tolist()
    online.remove('cash')
    online = [int(x[:-3]) for x in online]
    inter = set(offline).intersection(set(online))
    holding_num.loc[date, 'intersection'] = len(inter)

check = (holding_num['intersection'] / holding_num.T).T
account_info.to_excel('/data/user/015664/AFuckingTrigger/online_stat/线上净值.xlsx')
holding_num.to_excel('/data/user/015664/AFuckingTrigger/online_stat/线上线下收盘持仓数.xlsx')
