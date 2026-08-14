# @Time : 2021/2/1 13:31
# @Author : Zhichen Lu
# @File : daily_stat.py

import configparser
from online_conf import init_conf_path,daily_out_path,holding_info_path,code_list_path
import pandas as pd
from dataApi.getData import get_minute_1factor
import numpy as np

account_info = {}
for date in [20210105, 20210106, 20210107, 20210108, 20210111, 20210112, 20210113, 20210114, 20210115, 20210118, 20210119, 20210120, 20210121, 20210122, 20210125, 20210126, 20210127, 20210128]:
    config = configparser.ConfigParser()
    config.read(init_conf_path + '%d.ini' % date)
    account_info[date] = dict(config['account_info'])
account_info = pd.DataFrame(account_info).T.astype(float)
account_info['线上净值'] = account_info['account_value']/account_info['account_value'].tolist()[0]

offline = pd.read_excel('/data/user/015664/AFuckingTrigger/限制买入和持仓/NoFutureInfoResShift/XGB_Light_OnlineTestOutSampleRevTriggerFilterHolding_AlphaTriggerPoolTop600_deal_ratio_0.1_per_ratio_0.0050VolConsider0105_0127OnlineLimit_UpBuy100_10bp_cost.xlsx')
offline = offline.set_index('date')['账户净值'].loc[:account_info.index[-1]]
offline.name = '线下账户净值'
account_info.index = offline.index[:account_info.shape[0]]
account_info = pd.concat([account_info,offline.replace(0,1)],axis=1)
account_info['追踪误差'] = (account_info['线上净值'].pct_change() -
                        account_info[ '线下账户净值'].pct_change()).apply(abs)

holding_vol = {}
cash = {}
for date in [20210105, 20210106, 20210107, 20210108, 20210111, 20210112, 20210113, 20210114, 20210115, 20210118, 20210119, 20210120, 20210121, 20210122, 20210125, 20210126, 20210127]:
    for bar in [1000,1030,1100,1300,1330,1400,1430]:
        bar_summary = pd.read_pickle(f'{daily_out_path}{date}/{bar}_summary.pkl')
        holding_vol[(date,bar)] = pd.Series(bar_summary['barly_holding_info'].set_index('Symbol')['NetPosition'],name=(date,bar))
        cash[(date,bar)] = bar_summary['bar_inital_cash']

holding_vol = pd.DataFrame(holding_vol).T
involved = holding_vol.sum()
involved = involved[involved>0]
holding_vol = holding_vol[involved.index]

close = get_minute_1factor('close',start_datetime=202101050925,end_datetime=202101131500,code_list=[int(x[:-3]) for x in holding_vol.columns])
close.columns = holding_vol.columns

holding_mv = close.loc[holding_vol.index]*holding_vol

cash = pd.Series(cash)

mv = pd.DataFrame({'holding':holding_mv.sum(axis=1),'cash':cash})
mv['total'] = mv.sum(axis=1)
mv['pct'] = mv['total'].pct_change()

online_holding = {}
for date in [20210105, 20210106, 20210107, 20210108, 20210111, 20210112, 20210113, 20210114, 20210115, 20210118, 20210119, 20210120, 20210121, 20210122, 20210125, 20210126, 20210127]:
    temp_holding = pd.read_pickle(f'{holding_info_path}{date}.pkl')
    online_holding[date] = temp_holding

online_holding = pd.DataFrame(online_holding).T


res_pn,cash_series = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/NoFutureInfoResShift/record/XGB_Light_daily_res_pn_0105_0127OnlineLimit.pkl')
offline_mv = res_pn.minor_xs('收盘持仓市值')
offline_mv.columns = [str(x).zfill(6)+'.SZ' if x<400000 else str(x)+'.SH' for x in offline_mv.columns]

holding_num = pd.DataFrame({'online':(online_holding.drop('cash',axis=1)>0).sum(axis=1),'offline':(offline_mv>0).sum(axis=1)})
holding_num = holding_num[:-1]
holding_num['intersection'] = np.nan
for date in holding_num.index:
    online,offline = online_holding.loc[date],offline_mv.loc[date]
    online,offline = online[online>0].index.tolist(),offline[offline>0].index.tolist()
    online.remove('cash')
    # online = [int(x[:-3]) for x in online]
    inter = set(offline).intersection(set(online))
    holding_num.loc[date,'intersection'] = len(inter)

check = (holding_num['intersection']/holding_num.T).T
check.columns = ['线上和交集重合比例','线下和交集重合比例',0]
holding_num.columns = ['线上收盘持仓数','线下收盘持仓数','交集']
holding_num = pd.concat([holding_num,check],axis=1)


def get_intersec(date,pre_date,tag = 'OutSampleOnlineLimit_XGB_Light_OnlineTest'):
    offline_signal, offline_pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_%s.pkl' % tag)
    code_list = pd.read_pickle(code_list_path+'%d.pkl'%pre_date)
    holding_info = pd.read_pickle(holding_info_path+'%d.pkl'%pre_date)
    holding_info.pop('cash')
    code_list = set(code_list).union(set(holding_info.keys()))
    code_list = [int(x[:-3]) for x in code_list]
    offline_bar_pred_ret = offline_pred_ret.loc[date,code_list]#.loc[1000]
    offline_signal = offline_signal[code_list]

    online_output = pd.read_pickle(daily_out_path+'/%d.pkl'%date)
    signal = pd.DataFrame()
    for time_point in [1000,1030,1100,1300,1330,1400,1430]:
        online_bar_pred_ret = online_output['pred_ret'][time_point]
        offline_bar_signal = offline_signal.loc[date].loc[time_point]
        offline_bar_signal = offline_bar_signal[offline_bar_signal]
        online_bar_pred_ret.index = [int(x[:-3]) for x in online_bar_pred_ret.index]
        online_bar_pred_ret = online_bar_pred_ret.mean(axis=1)

        online_bar_signal = online_output['signal'][time_point]

        online_bar_signal.index = [int(x[:-3]) for x in online_bar_signal.index]

        online_bar_signal.loc[:] = True
        bar = pd.DataFrame({'online':online_bar_signal,'offline':offline_bar_signal})
        bar = bar.reset_index()
        bar['time'] = time_point
        bar = bar.set_index(['time','index'])
        signal = signal.append(bar.fillna(False))

    isolation_pool = pd.read_excel('/data/group/800319/strategy_local_path/restrict_list/隔离池20201010.xls')['证券代码'].astype(int)
    black_name_list = pd.read_excel('/data/group/800319/strategy_local_path/restrict_list/黑名单20201010.xls')['证券代码'].astype(int)
    unavailable_pool = set(isolation_pool).union(set(black_name_list))
    offline_unavailabel_stk = set([x[1] for x in signal.index]).intersection(set(unavailable_pool))

    signal = signal.swaplevel(0,1)
    signal.loc[list(offline_unavailabel_stk)] = np.nan
    signal = signal.dropna()>0.5
    inter_sec = signal[(signal['online'])&(signal['offline'])]
    XOR =  signal[~((signal['online'])&(signal['offline']))]
    signal_info = signal.sum()
    signal_info['intersection'] = inter_sec.shape[0]
    return signal_info,XOR

date_list = [20210105, 20210106, 20210107, 20210108, 20210111, 20210112, 20210113, 20210114, 20210115, 20210118, 20210119, 20210120, 20210121, 20210122, 20210125, 20210126, 20210127]
pre_date_list = [20210104]+date_list[:-1]
signal_stat = {}
for date,pre_date in list(zip(date_list,pre_date_list)):
    signal_stat[date],_ = get_intersec(date,pre_date)
    print(date)

signal_stat = pd.DataFrame(signal_stat).T
signal_stat['online_inter_ratio'] = signal_stat['intersection']/signal_stat['online']
signal_stat['offline_inter_ratio'] = signal_stat['intersection']/signal_stat['offline']
signal_stat.columns=['线上信号数','线下信号数','交集','交集占线上信号比例','交集占线下信号比例']



with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/online_stat_v20210219/1月信号回测结果统计_线上_线下.xlsx') as writer:
    signal_stat.to_excel(writer,sheet_name='信号重合统计')
    account_info.to_excel(writer,sheet_name='线上净值')
    holding_num.to_excel(writer,sheet_name='线上线下收盘持仓数')
writer.close()
