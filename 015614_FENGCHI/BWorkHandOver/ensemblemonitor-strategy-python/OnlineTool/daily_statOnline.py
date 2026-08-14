# @Time : 2021/2/1 13:31
# @Author : Zhichen Lu
# @File : daily_stat.py

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

def get_holding_num(start_backtest_date,pre_date,date_list):
    holding_vol = {}
    # cash = {}
    for date in date_list:
        final_summary = None
        if os.path.exists(f'{daily_out_path}/{date}.pkl'):
            final_summary = pd.read_pickle(f'{daily_out_path}/{date}.pkl')
        for bar in [1000,1030,1100,1300,1330,1400,1430]:

            if not final_summary is None:
                holding_vol[(date, bar)] = pd.Series(final_summary['barly_holding_info'][bar].set_index('Symbol')['NetPosition'], name=(date, bar))
                # cash[(date, bar)] = bar_summary['bar_inital_cash']
            elif os.path.exists(f'{daily_out_path}{date}/{bar}_summary.pkl'):
                bar_summary = pd.read_pickle(f'{daily_out_path}{date}/{bar}_summary.pkl')
                # raise Exception('No bar_summary')
                holding_vol[(date,bar)] = pd.Series(bar_summary['barly_holding_info'].set_index('Symbol')['NetPosition'],name=(date,bar))
                # cash[(date,bar)] = bar_summary['bar_inital_cash']
            else:
                raise Exception('No Summary file')
    holding_vol = pd.DataFrame(holding_vol).T
    involved = holding_vol.sum()
    involved = involved[involved>0]
    holding_vol = holding_vol[involved.index]

    # close = get_minute_1factor('close',start_datetime=start_backtest_date*10000+925,end_datetime=pre_date*10000+1500,code_list=[int(x[:-3]) for x in holding_vol.columns])
    close = get_minute_pickle('close',date_list=get_date_range(start_backtest_date,pre_date),code_list=[int(x[:-3]) for x in holding_vol.columns])
    close.columns = holding_vol.columns

    # holding_mv = close.loc[holding_vol.index]*holding_vol
    # cash = pd.Series(cash)
    # mv = pd.DataFrame({'holding':holding_mv.sum(axis=1),'cash':cash})
    # mv['total'] = mv.sum(axis=1)
    # mv['pct'] = mv['total'].pct_change()

    online_holding = {}
    for date in date_list:
        temp_holding = pd.read_pickle(f'{holding_info_path}{date}.pkl')
        online_holding[date] = temp_holding

    online_holding = pd.DataFrame(online_holding).T

    res_pn,offline_buy_time = pd.read_pickle(f'{offline_res_path}daily_res_pn/{pre_date}.pkl')
    offline_mv = res_pn.minor_xs('收盘持仓市值')
    offline_mv.columns = [str(x).zfill(6)+'.SZ' if x<400000 else str(x)+'.SH' for x in offline_mv.columns]
    offline_mv = offline_mv.reindex(online_holding.index)
    holding_num = pd.DataFrame({'online':(online_holding.drop('cash',axis=1)>=100).sum(axis=1),'offline':(offline_mv>0).sum(axis=1)})

    holding_num['intersection'] = np.nan
    online_extra = {}
    offline_extra = {}
    for date in holding_num.index:
        online,offline = online_holding.loc[date],offline_mv.loc[date]
        online,offline = online[online>100].index.tolist(),offline[offline>0].index.tolist()
        if 'cash' in online:
            online.remove('cash')
        # online = [int(x[:-3]) for x in online]
        inter = set(offline).intersection(set(online))
        holding_num.loc[date,'intersection'] = len(inter)

        online_extra[date] = '.'.join([str(x) for x in sorted(list(set(online) - set(offline)))])
        offline_extra[date] = ','.join([str(x) for x in sorted(list(set(offline) - set(online)))])

    check = (holding_num['intersection']/holding_num.T).T
    check.columns = ['线上和交集重合比例','线下和交集重合比例',0]
    holding_num.columns = ['线上收盘持仓数','线下收盘持仓数','交集']
    holding_num['线上持有-线下未持有'] = pd.Series(online_extra)
    holding_num['线下持有-线上未持有'] = pd.Series(offline_extra)
    holding_num = pd.concat([holding_num,check],axis=1)

    online_buy_time_info = pd.read_pickle(buy_time_info_path+'%d.pkl'%pre_date)
    online_buy_time_info,offline_buy_time = pd.Series(online_buy_time_info),pd.Series(offline_buy_time)
    online_buy_time_info = online_buy_time_info.apply(lambda x : x[0]*10000+x[1])
    offline_buy_time.index = [str(x).zfill(6)+'.SZ' if x<400000 else str(x)+'.SH' for x in offline_buy_time.index]
    buy_time_info = pd.DataFrame({'online':online_buy_time_info,'offline':offline_buy_time})


    return holding_num,buy_time_info

def get_intersec(date,pre_date,file_name):
    offline_signal, offline_pred_ret = pd.read_pickle(file_name)
    code_list = pd.read_pickle(code_list_path+'%d.pkl'%pre_date)
    holding_info = pd.read_pickle(holding_info_path+'%d.pkl'%pre_date)
    holding_info.pop('cash')
    code_list = set(code_list).union(set(holding_info.keys()))
    code_list = [int(x[:-3]) for x in code_list]
    try:
        offline_bar_pred_ret = offline_pred_ret.loc[date,code_list]#.loc[1000]
    except:
        print(1)
    offline_signal = offline_signal.reindex(code_list,axis=1).fillna(False)
    if date==20210730:
        print(1)
        from dataApi.getData import trans_windcode2int
        holding = pd.read_pickle(f'{holding_info_path}{get_pre_trade_date(date)}.pkl')
        holding.pop('cash')
        offline_signal[list(map(trans_windcode2int, holding.keys()))] = False
    signal = pd.DataFrame()

    for time_point in [1000,1030,1100,1300,1330,1400,1430]:
        if os.path.exists(daily_out_path + '/%d.pkl' % date):
            online_output = pd.read_pickle(daily_out_path + '/%d.pkl' % date)
            online_bar_signal = online_output['signal'][time_point]
        elif os.path.exists(f'{daily_out_path}{date}/{time_point}_summary.pkl'):
            online_output = pd.read_pickle(f'{daily_out_path}/{date}/{time_point}_summary.pkl')
            online_bar_signal = online_output['signal']#[time_point]
        else:
            online_bar_signal = pd.Series()
        offline_bar_signal = offline_signal.loc[date].loc[time_point]

        offline_bar_signal = offline_bar_signal[offline_bar_signal]

        online_bar_signal.index = [int(x[:-3]) for x in online_bar_signal.index]

        online_bar_signal.loc[:] = True
        bar = pd.DataFrame({'online':online_bar_signal,'offline':offline_bar_signal})
        bar = bar.reset_index()
        bar['time'] = time_point
        bar = bar.set_index(['time','index'])
        signal = signal.append(bar.fillna(False))
    # triggered_stk_num_online =


    unavailable_pool = pd.read_pickle(path_conf['local_config_path']+'restrict_list.pkl')
    offline_unavailabel_stk = set([x[1] for x in signal.index]).intersection(set(unavailable_pool))
    if date==20210702:
        print(1)
    signal = signal.swaplevel(0,1)
    signal.loc[list(offline_unavailabel_stk)] = np.nan
    signal = signal.dropna()>0.5
    inter_sec = signal[(signal['online'])&(signal['offline'])]
    XOR =  signal[~((signal['online'])&(signal['offline']))]
    signal_info = signal.sum()
    signal_info['intersection'] = inter_sec.shape[0]
    if date==20210810:
        print(1)
    offline_trigger_stk = (offline_signal.groupby('date').sum() > 0).loc[date]
    offline_trigger_stk = offline_trigger_stk[offline_trigger_stk].index.tolist()
    online_trigger_stk = (signal.groupby(level=0).sum()['online']>0)
    online_trigger_stk = online_trigger_stk[online_trigger_stk].index.tolist()

    signal_info['线下触发股票数量'] = len(offline_trigger_stk)
    signal_info['线上触发股票数量'] = len(online_trigger_stk)

    signal_info['线上触发线下未触发'] = ','.join([str(x) for x in sorted(list(set(online_trigger_stk)-set(offline_trigger_stk)))])
    signal_info['线下触发线上未触发'] = ','.join([str(x) for x in sorted(list(set(offline_trigger_stk)-set(online_trigger_stk)))])
    return signal_info,XOR


def get_signal_stat(date_list,tag):
    pre_date_list = [get_pre_trade_date(date_list[0])]+date_list[:-1]
    signal_stat = {}
    for date,pre in list(zip(date_list,pre_date_list)):
        signal_stat[date],_ = get_intersec(date, pre, f'{offline_signal_path}/signal_OutSample_{tag}_OnlineTest_{date}.pkl')
        print(date)

    signal_stat = pd.DataFrame(signal_stat).T
    signal_stat['online_inter_ratio'] = signal_stat['intersection']/signal_stat['online']
    signal_stat['offline_inter_ratio'] = signal_stat['intersection']/signal_stat['offline']
    signal_stat.columns=['线上信号数','线下信号数','交集','交集占线上信号比例','交集占线下信号比例']
    return signal_stat

def get_signal_stat_recent(date_list,tag):
    pre_date_list = [get_pre_trade_date(date_list[0])]+date_list[:-1]
    signal_stat = {}
    for date,pre in list(zip(date_list,pre_date_list)):
        if date==20220420:
            print(1)
        signal_stat[date],_ = get_intersec(date, pre, f'{offline_signal_path}/signal_OutSample_{tag}_OnlineTest_{date_list[-1]}.pkl')
        print(date)

    signal_stat = pd.DataFrame(signal_stat).T
    signal_stat['online_inter_ratio'] = signal_stat['intersection']/signal_stat['online'].replace(0,np.nan)
    signal_stat['offline_inter_ratio'] = signal_stat['intersection']/signal_stat['offline'].replace(0,np.nan)
    signal_stat = signal_stat.rename(columns={
        'online':'线上信号数', 'offline':'线下信号数', 'intersection':'交集', 'online_inter_ratio':'交集占线上信号比例',
        'offline_inter_ratio':'交集占线下信号比例'
    })#.columns=['线上信号数','线下信号数','交集','交集占线上信号比例','交集占线下信号比例']
    return signal_stat

def get_basic_indicator_compare(path_conf,file_name,date_list,out=None):
    local_config_path, holding_info_path, hyper_param_path, code_list_path, model_config_path, buy_time_info_path, \
    vol_info_path, init_conf_path, ratio_path, matrix_conf, condition_path = \
        [path_conf[x] for x in
         ['local_config_path', 'holding_info_path', 'hyper_param_path', 'code_list_path', 'model_config_path', 'buy_time_info_path',
          'vol_info_path', 'init_conf_path', 'ratio_path', 'matrix_conf', 'condition_path']]

    offline_indicator = pd.read_pickle(file_name)

    # date_list = [20220110,20220111]#get_date_range(20210913, 20210928)
    online_indicator = {}
    for date in date_list:
        temp = pd.read_pickle(f'{daily_out_path}/{date}.pkl')
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

def main_compare(today=None,tag= 'XGB_Cat_Light',start_backtest_date = 20210406,cash_flow={},extra_tag='',basic_indicator_file=None):
    #20210302
    if today is None:
        today = int(datetime.date.today().strftime('%Y%m%d'))
    pre_date = get_pre_trade_date(today)
    date_list = get_date_range(start_backtest_date, pre_date)
    # signal_stat = get_signal_stat_recent(date_list,tag)
    signal_stat = get_signal_stat_recent(date_list,tag)
    account_info = get_account_compare(today,pre_date,start_backtest_date,date_list,tag)
    account_info['累计收益'] = account_info['线上账户总市值'] - pd.Series(cash_flow).reindex(sorted(list(set(cash_flow.keys()).union(account_info.index)))).fillna(0).cumsum()


    holding_num,_ = get_holding_num(start_backtest_date,pre_date,date_list)
    if not os.path.exists(f'{out_path}{pre_date}/'):
        os.mkdir(f'{out_path}{pre_date}/')
    out_name = f'{out_path}{pre_date}/{extra_tag}对比{pre_date}.xlsx'
    with pd.ExcelWriter(out_name) as writer:
        signal_stat.to_excel(writer, sheet_name='信号重合统计')
        account_info.to_excel(writer, sheet_name='线上净值')
        holding_num.to_excel(writer, sheet_name='线上线下收盘持仓数')
        if basic_indicator_file:
            compare = get_basic_indicator_compare(path_conf,basic_indicator_file,date_list)
            compare.to_excel(writer,sheet_name='基础指标对比')

    writer.close()
    send_file(['015664'],out_name)

out_path = '/data/user/015664/AFuckingTrigger/实盘/'
offline_res_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/'
offline_signal_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/'
path_conf = get_path_conf('/data/group/800319/strategy_local_path3_FixVersion0421/')
# path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
# path_conf = get_path_conf('/data/user/015664/StrategyBackUp/strategy_local_path3DailyBackup/')
init_conf_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path = [path_conf[x] for x in\
                                                'init_conf_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path'.split(',')]
daily_out_path = '/data/user/015664/StrategyBackUp/strategy_local_path3DailyBackup/daily_output/'


# out_path = '/data/user/015664/AFuckingTrigger/仿真/'
# offline_res_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测线下跟踪/'
# offline_signal_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/仿真跟踪线下信号/'
# path_conf = get_path_conf('/data/group/800319//strategy_local_path3_ForMix20210803/')
# hyper_param_path,init_conf_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path = [path_conf[x] for x in\
#                                                 'hyper_param_path,init_conf_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path'.split(',')]
#

# base_dir =  '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测Ray/'
# path_conf = get_path_conf('/data/group/800319/strategy_local_path3_ForMixSim/')
# base_dir =  '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测Matrix/'


#
# tag = f''
# base_dir =  f'/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测Extra{tag}_Sim/'
# path_conf = get_path_conf(f'/data/group/800319/strategy_local_path3_ForExtraSim/')
# out_path = f'{base_dir}/比对/'
# if not os.path.exists(out_path):
#     os.makedirs(out_path)
# offline_res_path = base_dir
# offline_signal_path = f'{base_dir}信号/'
# hyper_param_path,init_conf_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path = [path_conf[x] for x in\
#                                                 'hyper_param_path,init_conf_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path'.split(',')]

if __name__ == '__main__':
    # main_compare(20211105,start_backtest_date=20211012,extra_tag='仿真混合因子Ray')

    main_compare(20220121,tag='XGBMonthlyV4WithSWMeanFixFixMIX_Cat_Light_Val',start_backtest_date=20220112,extra_tag=f'仿真回测ForExtraSim',
                 basic_indicator_file='/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测Extra_Sim/barly_condition_indicator/XGBMonthlyV4WithSWMeanFixFixMIX_Cat_Light_Val_OnlineTestOutSampleRevTriggerFilterHolding_AlphaTriggerPoolTop600_deal_ratio_0.1_per_ratio_0.0050_20220120OnlineTracing.pkl')
    # main_compare(20211026,start_backtest_date=20210406,extra_tag='test')