# @Time : 2021/7/1 19:24
# @Author : Zhichen Lu
# @File : OnlineCompare.py
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range,get_pre_trade_date
# from online_conf import path_for_930
from dataApi.sendInfo import send_file
path_for_930 = '/data/user/015664/StrategyBackUp/strategy_local_path3DailyBackup/FolderFor930/'
base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/930/'
def get_acoount_comapre(start_date,date):
    offline_account = pd.read_excel(f'{base_path}Back930_10bp_cost_{date}.xlsx',index_col=0)
    offline_account = offline_account[['收盘账户市值','账户资金','持仓股票数','收盘持仓市值','账户净值']]
    offline_account.columns =['线下账户总市值', '线下剩余现金', '线下收盘持仓数', '线下持仓市值', '线下净值']


    account_info = {}
    for day in get_date_range(get_pre_trade_date(start_date),date):
        # day = 20210611
        next_day = get_pre_trade_date(day,-1)
        account_value = pd.read_pickle(f'{path_for_930}{next_day}/StrategyIn/account_info{next_day}.pkl')
        strategy_init = pd.read_pickle(f'{path_for_930}{next_day}/StrategyIn/init{next_day}.pkl')
        account_info[day] = {'线上账户总市值':account_value['account_value'],
                             '线上剩余现金':strategy_init['cash'],
                             '线上收盘持仓数':account_value['holding_num']
                             }
    account_info = pd.DataFrame(account_info).T.astype(float)
    account_info['线上持仓市值'] = account_info['线上账户总市值'] - account_info['线上剩余现金']
    account_info['线上净值'] = account_info['线上账户总市值'] / account_info['线上账户总市值'] .tolist()[0]
    offline_account['线下净值'] = offline_account['线下账户总市值']/account_info['线上账户总市值'] .tolist()[0]

    date_list = get_date_range(start_date,date)
    account_info = pd.concat([account_info, offline_account], axis=1)
    account_info['追踪误差'] = (account_info['线上净值'].reindex([get_pre_trade_date(start_date)] + date_list).fillna(1).pct_change() -
                            account_info['线下净值'].reindex([get_pre_trade_date(start_date)] + date_list).fillna(1).pct_change()).apply(abs)
    return account_info

def get_interact(start_date,date):
    # start_date = 20210611
    # date = 20210630

    online_holding = {}
    for day in get_date_range(start_date,date):
        temp_holding = pd.read_pickle(f'{path_for_930}{day}/StrategyOut/holding{day}.pkl')
        online_holding[day] = temp_holding

    online_holding = pd.DataFrame(online_holding).T

    res_pn, offline_buy_time = pd.read_pickle(f'{base_path}daily_res_pn/{date}.pkl')
    offline_mv = res_pn.minor_xs('收盘持仓市值')
    offline_mv.columns = [str(x).zfill(6) + '.SZ' if x < 400000 else str(x) + '.SH' for x in offline_mv.columns]

    holding_num = pd.DataFrame({
                                '线上收盘持仓数': (online_holding.drop('cash', axis=1) > 0).sum(axis=1),
                                '线下收盘持仓数': (offline_mv > 0).sum(axis=1)})
    holding_num['交集'] = np.nan
    offline_mv = offline_mv.reindex(holding_num.index)

    for date in holding_num.index:
        online,offline = online_holding.loc[date],offline_mv.loc[date]
        online,offline = online[online>0].index.tolist(),offline[offline>0].index.tolist()
        if 'cash' in online:
            online.remove('cash')
        # online = [int(x[:-3]) for x in online]
        inter = set(offline).intersection(set(online))
        holding_num.loc[date,'交集'] = len(inter)

    check = (holding_num['交集'] / holding_num.T).T
    check.columns = ['线上和交集重合比例', '线下和交集重合比例', 0]
    holding_num['线上0股数量'] = ((online_holding.drop('cash', axis=1) > 0)*(online_holding.drop('cash', axis=1) <=100)>0.5).sum(axis=1)
    holding_num = pd.concat([holding_num, check.drop(0,axis=1)], axis=1)
    return holding_num

def calc_930_compare(start_date,date,cash_added):

    holding_num = get_interact(start_date,date)
    account_info = get_acoount_comapre(start_date,date)
    print(date)
    account_info['累计收益'] = account_info['线上账户总市值']-pd.Series(cash_added).reindex(account_info.index).fillna(0).cumsum()
    with pd.ExcelWriter(f'{base_path}比对/930线上线比对{date}.xlsx') as writer:
        account_info.to_excel(writer,'净值比对')
        holding_num.to_excel(writer,'线上线下收盘持仓数')
    writer.close()
    send_file(['015664'],f'{base_path}比对/930线上线比对{date}.xlsx')


# cash_added = {20210702:1000000,20210705:7000000,20210720:22000000,20210727:-7500000,
#               20210730:-15000000-173508.90871492773,20210802:4500000,20210804:-4500000,
#               20210817:-4692212.966834789,20210825:3000000,20210827:4500000}
#
# calc_930_compare(20210705,20210906,cash_added)
