# @Time : 2021/2/1 13:31
# @Author : Zhichen Lu
# @File : daily_stat.py

import configparser
# from online_conf import init_conf_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path
from ExtraTools import get_path_conf
import pandas as pd
from dataApi.getData import get_minute_1factor,get_minute_pickle,trans_int2windcode,trans_windcode2int
import numpy as np
import datetime,os
from dataApi.tradeDate import get_pre_trade_date,get_date_range
from dataApi.sendInfo import send_file
from xquant.factordata import FactorData
from ExtraTools import get_nonfix_in_val
from tqdm import tqdm

s = FactorData()



def get_account_compare(today,pre_date,start_backtest_date,date_list,tag,base_dir,strategy_base_path):
    account_info = {}
    for date in date_list+[today]:
        config = get_nonfix_in_val('ini',date,strategy_base_path)
        account_info[date] = dict(config['account_info'])
        account_info[date]['cash'] = dict(config['strategy_init'])['cash']
    account_info = pd.DataFrame(account_info).T.astype(float).rename(columns={'account_value':'线上账户总市值','cash':'线上剩余现金','holding_num':'线上收盘持仓数'})
    account_info['线上持仓市值'] = account_info['线上账户总市值'] - account_info['线上剩余现金']
    account_info['线上净值'] = account_info['线上账户总市值']/account_info['线上账户总市值'].tolist()[0]
    account_info = account_info.shift(-1).reindex(date_list)
    offline = pd.read_excel(f'{base_dir}{tag}_{pre_date}_VolConsider_UpBuy100_10bp_cost.xlsx' )
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

def get_holding_num(date_list,tag,base_dir,strategy_base_path):
    holding_vol = {}
    record = pd.read_pickle(f'{base_dir}/record/record_{tag}_{date_list[-1]}_VolConsider_UpBuy100_10bp_cost.pkl')[:5]
    offline_holding_info = record[4]

    online_num,offline_num,intersection,online_extra,offline_extra = {},{},{},{},{}
    for date in tqdm(date_list,desc='统计持仓重合情况'):
        for bar in [1000,1030,1100,1300,1330,1400,1430,1500]:
            if bar == 1500:
                bar_holding = get_nonfix_in_val('holding_info', get_pre_trade_date(date, -1), strategy_base_path)

            elif os.path.exists(f'{strategy_base_path}/daily_output/{date}/{bar}_summary.pkl'):

                bar_summary = pd.read_pickle(f'{strategy_base_path}/daily_output/{date}/{bar}_summary.pkl')
                bar_holding = pd.Series(bar_summary['barly_holding_info'].set_index('Symbol')['NetPosition'],name=(date,bar))
                bar_holding = bar_holding[bar_holding>=100]
            else:
                bar_holding = pd.Series()


            holding_vol[(date, bar)] = bar_holding.copy()
            bar_holding = set(dict(bar_holding).keys()) - set(['cash'])

            bar_offline_holding = set(map(trans_int2windcode,set(offline_holding_info[(date,bar)].keys())-set(['cash'])))
            online_num[(date,bar)] = len(bar_holding)
            offline_num[(date,bar)] = len(bar_offline_holding)
            intersec = bar_offline_holding.intersection(bar_holding)
            intersection[(date,bar)] = len(intersec)
            online_extra[(date,bar)] = ','.join(sorted(list(bar_holding - bar_offline_holding)))
            offline_extra[(date,bar)] = ','.join(sorted(list(bar_offline_holding - bar_holding)))



    stat = pd.DataFrame({
        '线上持仓数量':online_num,
        '线下持仓数量':offline_num,
        '交集':intersection,
        '线上重合率':pd.Series(intersection)/pd.Series(online_num),
        '线下重合率':pd.Series(intersection)/pd.Series(offline_num),
        '线上-线下':online_extra,
        '线下-线上':offline_extra,
    })

    holding_vol = pd.DataFrame(holding_vol).T.drop('cash',axis=1)
    holding_vol.columns = holding_vol.columns.map(lambda x: int(x[:6]))
    offline_holding_info = pd.DataFrame(offline_holding_info).T.drop('cash',axis=1)
    union_stk = sorted(list(set(holding_vol.columns).union(offline_holding_info.columns)))

    holding_vol = holding_vol.reindex(union_stk,axis=1)
    offline_holding_info = offline_holding_info.reindex(union_stk,axis=1)

    return stat,holding_vol,offline_holding_info

def get_order_info(date_list,tag,base_dir,strategy_base_path):

    record = pd.read_pickle(f'{base_dir}/record/record_{tag}_{date_list[-1]}_VolConsider_UpBuy100_10bp_cost.pkl')[:5]
    order_info = record[-2]
    stat = {}
    for tag in ['buy','sell']:
        online_num,offline_num,intersection,online_extra,offline_extra = {},{},{},{},{}
        for date in tqdm(date_list,desc=''):
            for bar in [1000,1030,1100,1300,1330,1400,1430]:
                bar_summary = pd.read_pickle(f'{strategy_base_path}/daily_output/{date}/{bar}_summary.pkl')
                if tag=='sell':
                    online_order = set(bar_summary[f'{tag}_order_record'][bar_summary[f'{tag}_order_record']>100].index.tolist())
                else:
                    online_order = set(bar_summary[f'{tag}_order_record'].index.tolist())

                offline_order = set(order_info[(date,bar)][f'{tag}_order']['sent_order'].index.map(trans_int2windcode).tolist())
                inter = online_order.intersection(offline_order)

                online_num[(date,bar)] = len(online_order)
                offline_num[(date,bar)] = len(offline_order)
                intersection[(date,bar)] = len(inter)
                online_extra[(date,bar)] = ','.join(sorted(list(online_order - offline_order)))
                offline_extra[(date,bar)] = ','.join(sorted(list(offline_order - online_order)))

        c_tag = '买入' if tag=='buy' else '卖出'

        stat[tag] = pd.DataFrame({
            f'线上_{c_tag}指令':online_num,
            f'线下_{c_tag}指令':offline_num,
            f'交集_{c_tag}':intersection,
            f'线上重合率_{c_tag}':pd.Series(intersection)/pd.Series(online_num),
            f'线下重合率_{c_tag}':pd.Series(intersection)/pd.Series(offline_num),
            f'线上-线下_{c_tag}':online_extra,
            f'线下-线上_{c_tag}':offline_extra,
        })

    return stat



def get_intersec(date,file_name,strategy_base_path):
    code_list = get_nonfix_in_val('code_list',date,strategy_base_path)#pd.read_pickle(code_list_path + '%d.pkl' % pre_date)
    holding_info = get_nonfix_in_val('holding_info',date,strategy_base_path)#pd.read_pickle(holding_info_path + '%d.pkl' % pre_date)
    bar_list = [1000,1030,1100,1300,1330,1400,1430]
    holding_info.pop('cash')
    code_list = set(code_list).union(set(holding_info.keys()))
    code_list = [int(x[:-3]) for x in code_list]

    offline_long = {}
    offline_short = {}
    offline_pred_ret = {}
    for i in range(1,9):
        temp_long = pd.read_pickle(f'{file_name}long/signal_long_{i}_pct_0.05.pkl')
        offline_long[i] = temp_long[0].loc[date].reindex(code_list,axis=1).fillna(False).stack()
        offline_pred_ret[i] = temp_long[1].loc[date].reindex(code_list,axis=1).stack()
        if i>=8:
            continue
        temp_short = pd.read_pickle(f'{file_name}short/signal_short_{i}_pct_0.pkl')
        offline_short[i] = temp_short[0].loc[date].reindex(code_list,axis=1).fillna(False).stack()

    offline_long = pd.DataFrame(offline_long).sort_index()
    offline_short = pd.DataFrame(offline_short).sort_index()

    online_long = {}
    online_short = {}

    online_pred_ret = {}
    # daily_summary = pd.read_pickle(f'{non_fix_path}daily_output/{date}/final_summary.pkl')
    output_path = f'{strategy_base_path}/daily_output/{date}/'
    final_summary = None
    for time_point in bar_list:
        # break
        if os.path.exists(f'{output_path}final_summary.pkl') and final_summary is None:
            final_summary = pd.read_pickle(f'{output_path}final_summary.pkl')
        if not final_summary is None:
            online_bar_long_signal = final_summary['long_signal'][time_point]
            online_bar_short_signal = final_summary['short_signal'][time_point]
            online_bar_pred_ret = {x:final_summary['pred_ret'][time_point][x].mean(axis=1) for x in final_summary['pred_ret'][time_point]}
        elif os.path.exists(f'{output_path}/{time_point}_summary.pkl'):
            bar_summary = pd.read_pickle(f'{output_path}/{time_point}_summary.pkl')
            online_bar_long_signal = bar_summary['long_signal']
            online_bar_short_signal = bar_summary['short_signal']
            online_bar_pred_ret = {x:bar_summary['pred_ret'][x].mean(axis=1) for x in bar_summary['pred_ret']}

        else:
            online_bar_long_signal = {i:pd.Series() for i in range(1,9) }
            online_bar_short_signal = {i:pd.Series() for i in range(1,9) }
            online_bar_pred_ret = {i:pd.Series() for i in range(1,9) }

        online_bar_long_signal = pd.DataFrame(online_bar_long_signal)
        online_bar_short_signal = pd.DataFrame(online_bar_short_signal)
        online_bar_long_signal.index = online_bar_long_signal.index.map(lambda x : int(x[:6]))
        online_bar_short_signal.index = online_bar_short_signal.index.map(lambda x : int(x[:6]))
        online_long[time_point] = online_bar_long_signal.reindex(code_list,index=0).notnull().stack(dropna=False)
        online_short[time_point] = online_bar_short_signal.reindex(code_list,index=0).notnull().stack(dropna=False)

        online_bar_pred_ret = pd.DataFrame(online_bar_pred_ret)
        online_bar_pred_ret.index = online_bar_pred_ret.index.map(lambda x : int(x[:6]))
        online_pred_ret[time_point] = online_bar_pred_ret.reindex(code_list,index=0).stack(dropna=False)


    online_long = pd.DataFrame(online_long).stack(dropna=False).unstack(level=1).swaplevel(0,1).sort_index()
    online_short = pd.DataFrame(online_short).stack(dropna=False).unstack(level=1).swaplevel(0,1).sort_index()
    online_pred_ret = pd.DataFrame(online_pred_ret).stack(dropna=False).unstack(level=1).swaplevel(0,1).sort_index()
    offline_pred_ret = pd.DataFrame(offline_pred_ret)

    nolimit = get_minute_pickle('limit_status',date_list=[date]).shift(1)
    nolimit = nolimit.loc[date].loc[bar_list].stack().loc[online_long.index]
    nolimit = nolimit[nolimit.fillna(0).isin([1,-1])]
    online_long.loc[nolimit.index] = False
    online_short.loc[nolimit.index]=False
    offline_long.loc[nolimit.index]=False
    offline_short.loc[nolimit.index]=False

    inter_sec_long = online_long&offline_long
    inter_sec_short = online_short&offline_short

    long_offline_extra = offline_long & ~online_long
    long_online_extra = ~offline_long & online_long
    long_difference = pd.DataFrame({
    'online':online_pred_ret[long_offline_extra | long_online_extra].stack(),
    'offline':offline_pred_ret[long_offline_extra | long_online_extra].stack(),
    'online_signal':online_long[long_offline_extra | long_online_extra].stack(),
        'offline_signal':offline_long[long_offline_extra | long_online_extra].stack(),
    })

    short_offline_extra = offline_short & ~online_short
    short_online_extra = ~offline_short & online_short
    short_difference = pd.DataFrame({
        'online': online_pred_ret[short_offline_extra | short_online_extra].stack(),
        'offline': offline_pred_ret[short_offline_extra | short_online_extra].stack(),
        'online_signal':online_short[short_offline_extra | short_online_extra].stack(),
        'offline_signal':offline_short[short_offline_extra | short_online_extra].stack(),
    })


    signal_info = pd.DataFrame({
        '线上看多信号数量':online_long.sum(),
        '线下看多信号数量':offline_long.sum(),
        '线上线下看多信号交集':inter_sec_long.sum(),
        '线上看空信号数量':online_short.sum(),
        '线下看空信号数量':offline_short.sum(),
        '线上线下看空信号交集':inter_sec_short.sum(),
    })
    long_ratio = (signal_info['线上线下看多信号交集']/signal_info[['线上看多信号数量','线下看多信号数量']].T).T.rename(columns={'线上看多信号数量':'线上看多重合率',
                                                                                         '线下看多信号数量':'线下看多重合率'})
    short_ratio = (signal_info['线上线下看空信号交集'] / signal_info[['线上看空信号数量', '线下看空信号数量']].T).T.rename(columns={'线上看空信号数量': '线上看空重合率',
                                                                                                         '线下看空信号数量': '线下看空重合率'})

    signal_info = pd.concat([signal_info,long_ratio,short_ratio],axis=1)

    return signal_info.reindex([ '线上看多信号数量','线下看多信号数量','线上线下看多信号交集','线上看多重合率','线下看多重合率',
        '线上看空信号数量','线下看空信号数量','线上线下看空信号交集','线上看空重合率','线下看空重合率'],axis=1),\
           long_difference.swaplevel(0,2).sort_index(),short_difference.swaplevel(0,2).sort_index()


def get_signal_stat_recent(date_list,tag,signal_date,base_dir,strategy_base):
    signal_stat = {}
    diff_long = {}
    diff_short = {}
    for date in tqdm(date_list,desc='统计信号交集...'):
        signal_stat[date],diff_long[date],diff_short[date] = get_intersec(date, f'{base_dir}/信号/{signal_date}/',strategy_base)
    signal_stat_df = pd.DataFrame({x:signal_stat[x].stack() for x in signal_stat}).T
    return signal_stat_df,diff_long,diff_short

def get_basic_indicator_compare(tag,base_dir,strategy_base_path,date_list,out=None):

    offline_indicator = pd.read_pickle(f'{base_dir}/record/record_{tag}_{date_list[-1]}_VolConsider_UpBuy100_10bp_cost.pkl')[-1]

    # date_list = [20220110,20220111]#get_date_range(20210913, 20210928)
    online_indicator = {}
    for date in date_list:
        temp = pd.read_pickle(f'{strategy_base_path}/daily_output/{date}/final_summary.pkl')
        online_indicator.update({(date, x): temp['extra_condition_param'][x] for x in temp['extra_condition_param']})

    online_indicator = pd.DataFrame(online_indicator).T.drop(['CYBZ', 'HS300', 'SZ50', 'ZX100', 'ZZ1000', 'ZZ500', 'ZZ800', 'ZZQZ', 'ZZZZ'], axis=1)
    offline_indicator = pd.DataFrame(offline_indicator).T
    if '__builtins__' in offline_indicator.columns:
        offline_indicator = offline_indicator.drop('__builtins__',axis=1)
    # offline_indicator['terminal_flag'] = offline_indicator['terminal_flag'].apply(lambda x: 1 - x)
    compare = pd.DataFrame({'线上': online_indicator.stack(), '线下': offline_indicator.stack()})
    compare = compare.stack().unstack(level=[-2, -1]).astype(float)
    check = compare.swaplevel(0,1,axis=1)
    diff = check['线上'].astype(float) - check['线下'].astype(float)
    diff.columns = pd.MultiIndex.from_tuples(diff.columns.map(lambda x:(x,'diff')))
    compare = pd.concat([compare,diff],axis=1).sort_index(axis=1,ascending=False)
    if out:
        # out_file = f'./{tag}_20220111参数比对_当天股票池.xlsx'
        compare.to_excel(out)
        send_file(['015664'], out)
    return compare

def main_compare(today=None,tag= 'XGB_Cat_Light',start_backtest_date = 20210406,
                 cash_flow={},extra_tag='',basic_indicator_file=None,base_dir=None,strategy_base_path=None,send_diff=False):
    #20210302
    if today is None:
        today = int(datetime.date.today().strftime('%Y%m%d'))
    pre_date = get_pre_trade_date(today)
    date_list = get_date_range(start_backtest_date, pre_date)
    # signal_stat = get_signal_stat_recent(date_list,tag)
    signal_stat,diff_long,diff_short = get_signal_stat_recent(date_list,tag,signal_date= pre_date,base_dir=base_dir,strategy_base=strategy_base_path)
    account_info = get_account_compare(today,pre_date,start_backtest_date,date_list,tag,base_dir,strategy_base_path)
    account_info['累计收益'] = account_info['线上账户总市值'] - pd.Series(cash_flow).reindex(sorted(list(set(cash_flow.keys()).union(account_info.index)))).fillna(0).cumsum()

    holding_num,online_holding,offline_holding = get_holding_num(date_list,tag,base_dir,strategy_base_path)
    order_stat = get_order_info(date_list,tag,base_dir,strategy_base_path)
    out_name = f'{base_dir}/{extra_tag}对比{pre_date}.xlsx'
    with pd.ExcelWriter(out_name) as writer:
        signal_stat.to_excel(writer, sheet_name='信号重合统计')
        signal_stat.swaplevel(0, 1, axis=1)[['线上看多重合率', '线下看多重合率', '线上看空重合率', '线下看空重合率']].sort_index().to_excel(writer, sheet_name='信号重合率')
        account_info.to_excel(writer, sheet_name='线上净值')
        holding_num.to_excel(writer, sheet_name='线上线下收盘持仓数')
        order_stat['buy'].to_excel(writer, sheet_name='买入指令比对')
        order_stat['sell'].to_excel(writer, sheet_name='卖出指令比对')
        if basic_indicator_file:
            compare = get_basic_indicator_compare(tag,base_dir,strategy_base_path,date_list)
            compare.to_excel(writer,sheet_name='基础指标对比')

    writer.close()
    send_file(['015664'],out_name)

    out_diff_name = f'{base_dir}/{extra_tag}个股预测值差异{pre_date}.xlsx'
    with pd.ExcelWriter(out_diff_name) as writer:
        key_list = sorted(list(diff_long.keys()))
        for date in key_list:
            diff_long[date].to_excel(writer,sheet_name=f'{date}_long')
        key_list = sorted(list(diff_short.keys()))
        for date in key_list:
            diff_short[date].to_excel(writer,sheet_name=f'{date}_short')
    writer.close()
    if send_diff:
        send_file(['015664'],out_diff_name)



# base_dir='/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测NonFix/'
# from online_conf import non_fix_path,non_fix_in_path,non_fix_output_path

if __name__ == '__main__':
    # main_compare(20220127,tag='XGB_DTC_Matrix_Light_Cat',start_backtest_date=20220113,base_dir='/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测NonFix8Model/',
    #              strategy_base_path='/data/group/800319/strategy_local_path_nonfix/',extra_tag='非固定窗口XGB剔除因子',send_diff=True)
    # main_compare(20220323,tag='XGB_DTC_Matrix_Light_Cat',start_backtest_date=20220316,base_dir='/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测NonFix8ModelSince0316/',
    #              strategy_base_path='/data/group/800319/strategy_local_path_nonfixBackUp20220322/',extra_tag='仿真跟踪',send_diff=True)
    main_compare(None, tag='XGB_DTC_Matrix_Light_Cat', start_backtest_date=20220323, base_dir='/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测NonFix8ModelDropProbFactor20220323/',
                 strategy_base_path='/data/group/800319/strategy_local_path_nonfix/', extra_tag='仿真跟踪', send_diff=True)


