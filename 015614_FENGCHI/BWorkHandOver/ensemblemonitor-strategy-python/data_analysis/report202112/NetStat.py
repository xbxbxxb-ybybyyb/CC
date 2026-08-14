# @Time : 2021/12/5 19:20
# @Author : Zhichen Lu
# @File : NetStat.py
import configparser
# from online_conf import init_conf_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path
from ExtraTools import get_path_conf
import pandas as pd
from dataApi.getData import get_minute_1factor,get_minute_pickle
import numpy as np
import datetime,os
from dataApi.tradeDate import get_pre_trade_date,get_date_range
from dataApi.sendInfo import send_file
from xquant.factordata import FactorData
s = FactorData()
out_path = '/data/user/015664/AFuckingTrigger/实盘/'
offline_res_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/'
offline_signal_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/'
path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
init_conf_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path = [path_conf[x] for x in\
                                                'init_conf_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path'.split(',')]


per_ratio_change = {
    20210402:0.005,
    20210525: 0.02,
    20210617:0.01,
    20210624:0.005,
    20210727:0.006,
    20210729:0.00167,
    20210730:0.005,
    20210803:0.003125,
    20210804:0.005,
}

cash_flow = {
    20210402: 2000000,
    20210413:28000000,
             20210420:-20000000,
            20210506:20000000,
            20210513:50000000,
             20210525:120000000,
             20210527:-170000000,
            20210603:50000000,
            20210604:70000000,
             20210616:-10000000,
             20210706:60000000,
            20210727:-50000000,
             20210730:-100000000-7925804.88,
             20210802:30000000,
             20210804:-30000000,
             20210817:-30859736.86,
            20210825:20000000,
             20210827:30000000,
            20210928:-36846732.2,
            20210930:36846732.2,
            20211015:-44401839.49,
            20211103:30000000,
            20211111:50000000,
            20211126:-80000000
             }
def get_account_compare(today,pre_date,start_backtest_date,date_list,tag):
    account_info = {}
    for date in date_list+[today]:
        config = configparser.ConfigParser()
        config.read(init_conf_path + '%d.ini' % date)
        account_info[date] = dict(config['account_info'])
        account_info[date]['cash'] = dict(config['strategy_init'])['cash']
    account_info = pd.DataFrame(account_info).T.astype(float).rename(columns={'account_value':'线上账户总市值','cash':'线上剩余现金','holding_num':'线上收盘持仓数'})
    account_info['线上持仓市值'] = account_info['线上账户总市值'] - account_info['线上剩余现金']
    account_info['线上净值'] = account_info['线上账户总市值']/account_info['线上账户总市值'].tolist()[0]
    account_info = account_info.shift(-1).reindex(date_list)
    offline = pd.read_excel(f'{offline_res_path}{tag}_OnlineTestOutSampleRevTriggerFilterHolding_AlphaTriggerPoolTop600_deal_ratio_0.1_per_ratio_0.0050VolConsiderOnlineLimit_UpBuy100_10bp_cost_%d.xlsx' % pre_date)
    offline = offline.set_index('date')[['收盘账户市值','账户资金','持仓股票数','收盘持仓市值','账户净值']].reindex(date_list)
    offline.columns =['线下账户总市值', '线下剩余现金', '线下收盘持仓数', '线下持仓市值', '线下净值']

    account_info = pd.concat([account_info,offline],axis=1)
    account_info['追踪误差'] = (account_info['线上净值'].reindex([get_pre_trade_date(start_backtest_date)]+date_list).fillna(1).pct_change() -
                            account_info[ '线下净值'].reindex([get_pre_trade_date(start_backtest_date)]+date_list).fillna(1).pct_change()).apply(abs)

    wind_a = s.get_factor_value('WIND_AIndexWindIndustriesEOD', S_INFO_WINDCODE=['881001.WI'])[['TRADE_DT', 'S_DQ_CLOSE']].set_index('TRADE_DT')
    wind_a = wind_a.sort_index().loc[account_info.index.astype(str)]
    wind_a.index = wind_a.index.astype(int)
    account_info['万德全A'] = wind_a[wind_a.columns[0]]

    return account_info

today=20211203
pre_date = 20211202
start_backtest_date = 20210406
date_list = get_date_range(start_backtest_date, pre_date)
tag = 'XGB_Cat_Light'

account_info = get_account_compare(today,pre_date,start_backtest_date,date_list,tag)
account_info['累计收益'] = account_info['线上账户总市值'] - pd.Series(cash_flow).reindex(sorted(list(set(cash_flow.keys()).union(account_info.index)))).fillna(0).cumsum()

account_info['仓位变化前市值'] = account_info['线上账户总市值'] - pd.Series(cash_flow).reindex(sorted(list(set(cash_flow.keys()).union(account_info.index)))).fillna(0)
account_info['今日单笔'] = account_info['线上账户总市值']*pd.Series(per_ratio_change).reindex(sorted(list(set(cash_flow.keys()).union(account_info.index)))).fillna(method='pad')
account_info['今日单笔'] = account_info['今日单笔'].apply(lambda x : max(x // 10000 * 10000, 10000)).shift(1)#.fillna(method='backfill')
account_info.loc[start_backtest_date,'今日单笔'] = 10000.
# account_info
signal_stat_path = '/data/user/015664/AFuckingTrigger/实盘/%d/成交明细及收盘持仓情况%d.xlsx'
account_info['昨日持仓收益'] = np.nan
account_info['今日买入收益'] = np.nan
account_info['折算比例'] = account_info['今日单笔'].shift(1)/account_info['今日单笔']


for idx,date in enumerate(date_list):
    daily_signal = pd.read_excel(signal_stat_path % (date, date), sheet_name=None)
    profit_detail, order_detail = daily_signal['收益明细'], daily_signal['委托成交明细']
    prof = profit_detail.groupby('类型').sum()['费后收益']
    if '当日买入'in prof.index:
        account_info.loc[date,'昨日持仓收益'] = prof.drop('当日买入').sum()#['当日卖出']+prof['隔夜持仓']
        account_info.loc[date,'今日买入收益'] = prof['当日买入'].sum()
    else:
        account_info.loc[date, '昨日持仓收益'] = prof.sum()  # ['当日卖出']+prof['隔夜持仓']
        account_info.loc[date, '今日买入收益'] = 0#prof['当日买入']
    account_info.loc[date,'明细累计收益'] = prof.sum()

account_info['折算后收益率'] = (account_info['昨日持仓收益'] + account_info['今日买入收益']*account_info['折算比例'])/account_info['仓位变化前市值'].shift(1)
account_info.loc[start_backtest_date,'折算后收益率'] = account_info.loc[start_backtest_date,'累计收益']/cash_flow[get_pre_trade_date(start_backtest_date)]
account_info['不考虑规模净值'] = (account_info['折算后收益率'] +1).cumprod()

#####################
account_info_930 = pd.read_excel(f'/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/930/Back930_10bp_cost_{pre_date}.xlsx',index_col=0)
account_info = account_info.rename(columns={'线上账户总市值':'线上账户总市值FIX','线上剩余现金':'线上剩余现金FIX','线上持仓市值':'线上持仓市值FIX',
                             '累计收益':'累计收益FIX'})
account_info['线上账户总市值930'] =account_info_930['收盘账户市值'].reindex(account_info.index).fillna(0)
account_info['线上剩余现金930'] =account_info_930['账户资金'].reindex(account_info.index).fillna(0)
account_info['线上持仓市值930'] =account_info_930['收盘持仓市值'].reindex(account_info.index).fillna(0)
account_info['累计收益930'] =account_info_930['累积收益'].reindex(account_info.index).fillna(0)

for each in ['线上账户总市值', '线上剩余现金', '线上持仓市值', '累计收益']:
    account_info[each] = account_info[f'{each}FIX']+account_info[f'{each}930']

account_info['按占资计算净值'] = 1+pd.Series(1,index=account_info.index).cumsum()*account_info['累计收益']/account_info['线上持仓市值'].cumsum()#(account_info['不考虑规模按占资计算收益率']+1).cumprod()
account_info['仓位'] = account_info['线上持仓市值FIX']/account_info['仓位变化前市值']

monthly = account_info.loc[:20211130].copy()
monthly.index = pd.to_datetime(monthly.index.astype(str))

montly_stat = pd.DataFrame({
    '按净值计算收益': monthly['不考虑规模净值'].resample('1m').last()/monthly['不考虑规模净值'].resample('1m').first() - 1,
    '按占资计算收益率':monthly['按占资计算净值'].resample('1m').size()*(monthly['累计收益'].resample('1m').last() - monthly['累计收益'].resample('1m').first())/monthly['线上持仓市值'].resample('1m').sum(),
    '收益额':monthly['累计收益'].resample('1m').last() - monthly['累计收益'].resample('1m').first(),
    '日均持仓市值':monthly['线上持仓市值'].resample('1m').mean(),
    '日均收益率':(monthly['累计收益'].resample('1m').last() - monthly['累计收益'].resample('1m').first())/monthly['线上持仓市值'].resample('1m').sum(),
    '万德全A收益率':monthly['万德全A'].resample('1m').last()/monthly['万德全A'].resample('1m').first() - 1,
    '平均仓位':monthly['仓位'].resample('1m').mean()
 })
# monthly['累计收益'].resample('1m').size()*(monthly['累计收益'].resample('1m').last() - monthly['累计收益'].resample('1m').first())/monthly['线上持仓市值'].resample('1m').sum()
montly_stat.index = montly_stat.index.map(lambda x : x.strftime('%Y%m'))
all_period = pd.DataFrame({
'按净值计算收益': monthly['不考虑规模净值'].resample('1Y').last()/monthly['不考虑规模净值'].resample('1Y').first() - 1,
    '按占资计算收益率': monthly['累计收益'].resample('1Y').size() * (monthly['累计收益'].resample('1Y').last() - monthly['累计收益'].resample('1Y').first()) / monthly['线上持仓市值'].resample(
        '1Y').sum(),
    '收益额': monthly['累计收益'].resample('1Y').last() - monthly['累计收益'].resample('1Y').first(),
    '日均持仓市值': monthly['线上持仓市值'].resample('1Y').mean(),
    '日均收益率': (monthly['累计收益'].resample('1Y').last() - monthly['累计收益'].resample('1Y').first()) / monthly['线上持仓市值'].resample('1Y').sum(),
'万德全A收益率':monthly['万德全A'].resample('1Y').last()/monthly['万德全A'].resample('1Y').first() - 1,
'平均仓位':monthly['仓位'].resample('1Y').mean()

})
all_period.index = ['上线以来']
montly_stat = montly_stat.append(all_period)

out_file = './历史净值跟踪_日频_月频20211215.xlsx'

with pd.ExcelWriter(out_file) as writer:
    account_info.to_excel(writer,sheet_name='账户日信息')
    montly_stat.to_excel(writer,sheet_name='账户月信息')
writer.close()

# account_info.to_excel(out_file)
send_file(['015664'],out_file)


