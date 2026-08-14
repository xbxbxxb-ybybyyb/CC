# @Time : 2021/4/27 9:32
# @Author : Zhichen Lu
# @File : intradaySignalStat.py

import sys
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator', '/data/user/015664/TriggeredTrading'])


# from online_conf import local_config_path, holding_info_path, code_list_path,daily_out_path
from dataApi.getData import get_minute_1factor, get_daily_1factor, trans_int2windcode
from dataApi.tradeDate import get_date_range, get_pre_trade_date
import pandas as pd
import numpy as np
from dataApi.sendInfo import send_file
from dataApi.getData import get_daily_1factor,get_ind_neutral
import os
from ExtraTools import get_path_conf

# signal_stat_path = '/data/user/015664/AFuckingTrigger/实盘/%d/成交明细及收盘持仓情况%d.xlsx'
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]


def get_signal_stat(date_list,base_path):
    path_conf = get_path_conf(base_path)
    local_config_path, holding_info_path, code_list_path, daily_out_path = [path_conf[x] for x in 'local_config_path,holding_info_path,code_list_path,daily_out_path'.split(',')]

    all_trigger_signal = []
    all_stock_pool_signal = []
    all_mkt_signal = []
    daily_stock_pool_vwap_profit = {}

    vwap = get_daily_1factor('vwap')
    adj_factor = get_daily_1factor('adjfactor')
    vwap_profit = (vwap * adj_factor).pct_change().shift(-1).loc[date_list]
    vwap_profit.columns = vwap_profit.columns.map(trans_int2windcode)
    for date in date_list:
        daily_summary = pd.read_pickle(f'{daily_out_path}{date}.pkl')
        profit_detail = pd.DataFrame(daily_summary['signal']).stack().reset_index().rename(columns={'level_1':'time','level_0':'证券代码'})#.set_index('level_0')
        profit_detail['date'] = date
        # daily_signal = pd.read_excel(signal_stat_path % (date, date), sheet_name=None)
        profit_detail = profit_detail.set_index(['date', 'time', '证券代码'])

        stock_pool = pd.read_pickle(f'{code_list_path}{get_pre_trade_date(date)}.pkl')
        holding_info = pd.read_pickle(f'{holding_info_path}{get_pre_trade_date(date)}.pkl')
        stock_pool = list(set(stock_pool).union(set(holding_info.keys())) - set(['cash']))
        close_adj = get_minute_1factor('close_badj', date, get_pre_trade_date(date, -1))
        close_adj = close_adj.swaplevel(0, 1).loc[bar_list].swaplevel(0, 1)
        ret = close_adj.pct_change(7).shift(-7)
        ret.columns = ret.columns.map(trans_int2windcode)
        ret = ret.loc[[date]].stack()
        stock_pool_ret = ret.swaplevel(0, 2).loc[stock_pool].swaplevel(0, 2)

        profit_detail['未来240分钟收益'] = ret.loc[profit_detail.index]
        all_trigger_signal.append(profit_detail[['未来240分钟收益']])
        all_mkt_signal.append(ret)
        all_stock_pool_signal.append(stock_pool_ret)

        daily_stock_pool_vwap_profit[date] = pd.DataFrame({'未来收益': vwap_profit.loc[date, stock_pool].sort_values(ascending=False),
                                                           '分层': (vwap_profit.loc[date, stock_pool].sort_values(ascending=False).rank(ascending=False) - 1) // 50})
        daily_stock_pool_vwap_profit[date]['是否触发'] = False
        daily_stock_pool_vwap_profit[date].loc[list(set(profit_detail.index.levels[2])), '是否触发'] = True
        print(date)

    all_trigger_signal = pd.concat(all_trigger_signal)
    all_mkt_signal = pd.concat(all_mkt_signal)
    all_stock_pool_signal = pd.concat(all_stock_pool_signal)

    all_trigger_signal['month'] = all_trigger_signal.index.map(lambda x : x[0]//100)
    all_mkt_signal = pd.DataFrame({
        'ret':all_mkt_signal,'month':all_mkt_signal.index.map(lambda x : x[0]//100)
    })
    all_stock_pool_signal = pd.DataFrame({
        'ret': all_stock_pool_signal, 'month': all_stock_pool_signal.index.map(lambda x: x[0] // 100)
    })

    all_trigger_signal['win'] = all_trigger_signal['未来240分钟收益']>0.0012
    all_mkt_signal['win'] = all_mkt_signal['ret']>0.0012
    all_stock_pool_signal['win'] = all_stock_pool_signal['ret']>0.0012

    daily_signal_stat = pd.DataFrame({'信号平均收益率': all_trigger_signal.groupby(level=0).mean()['未来240分钟收益'],
                                      '股票池可交易信号平均收益率': all_stock_pool_signal.groupby(level=0).mean()['ret'],
                                      '全市场可交易信号平均收益率': all_mkt_signal.groupby(level=0).mean()['ret'],
                                      '信号数量': all_trigger_signal.groupby(level=0).size()
                                      })
    daily_signal_stat.loc['全时段'] = pd.Series({'信号平均收益率': all_trigger_signal.mean()['未来240分钟收益'],
                                              '股票池可交易信号平均收益率': all_stock_pool_signal.mean()['ret'],
                                              '全市场可交易信号平均收益率': all_mkt_signal.mean()['ret'],
                                              '信号数量': all_trigger_signal.shape[0],
                                              })

    daily_signal_win_rate = pd.DataFrame({'信号胜率': all_trigger_signal.groupby(level=0).mean()['win'],
                                          '股票池可交易信号胜率': all_stock_pool_signal.groupby(level=0).mean()['win'],
                                          '全市场可交易信号胜率': all_mkt_signal.groupby(level=0).mean()['win']})
    daily_signal_win_rate.loc['全时段'] = pd.Series({'信号胜率': all_trigger_signal['win'].mean(),
                                                  '股票池可交易信号胜率': all_stock_pool_signal['win'].mean(),
                                                  '全市场可交易信号胜率': all_mkt_signal['win'].mean()})

    opputunity = pd.DataFrame({'盈利信号数量': all_trigger_signal.groupby(level=0).sum()['win'],
                               '股票池可盈利机会数量': all_stock_pool_signal.groupby(level=0).sum()['win'],
                               '全市场可盈利机会数量': all_mkt_signal.groupby(level=0).sum()['win']})
    opputunity.loc['全时段'] = pd.Series({'盈利信号数量': all_trigger_signal.sum()['win'],
                                       '股票池可盈利机会数量': all_stock_pool_signal.sum()['win'],
                                       '全市场可盈利机会数量': all_mkt_signal.sum()['win']})
    opputunity['信号命中率'] = opputunity['盈利信号数量']/opputunity['股票池可盈利机会数量']
    opputunity['股票池命中率'] = opputunity['股票池可盈利机会数量']/opputunity['全市场可盈利机会数量']


    ##################monthly
    monthly_signal_stat = pd.DataFrame({'信号平均收益率': all_trigger_signal.groupby('month').mean()['未来240分钟收益'],
                                      '股票池可交易信号平均收益率': all_stock_pool_signal.groupby('month').mean()['ret'],
                                      '全市场可交易信号平均收益率': all_mkt_signal.groupby('month').mean()['ret'],
                                      '信号数量': all_trigger_signal.groupby('month').size()
                                      })
    monthly_signal_stat.loc['全时段'] = pd.Series({'信号平均收益率': all_trigger_signal.mean()['未来240分钟收益'],
                                              '股票池可交易信号平均收益率': all_stock_pool_signal.mean()['ret'],
                                              '全市场可交易信号平均收益率': all_mkt_signal.mean()['ret'],
                                              '信号数量': all_trigger_signal.shape[0],
                                              })

    monthly_signal_win_rate = pd.DataFrame({'信号胜率': all_trigger_signal.groupby('month').mean()['win'],
                                          '股票池可交易信号胜率': all_stock_pool_signal.groupby('month').mean()['win'],
                                          '全市场可交易信号胜率': all_mkt_signal.groupby('month').mean()['win']})
    monthly_signal_win_rate.loc['全时段'] = pd.Series({'信号胜率': all_trigger_signal['win'].mean(),
                                                  '股票池可交易信号胜率': all_stock_pool_signal['win'].mean(),
                                                  '全市场可交易信号胜率': all_mkt_signal['win'].mean()})

    monthly_opputunity = pd.DataFrame({'盈利信号数量': all_trigger_signal.groupby('month').sum()['win'],
                               '股票池可盈利机会数量': all_stock_pool_signal.groupby('month').sum()['win'],
                               '全市场可盈利机会数量': all_mkt_signal.groupby('month').sum()['win']})
    monthly_opputunity.loc['全时段'] = pd.Series({'盈利信号数量': all_trigger_signal.sum()['win'],
                                       '股票池可盈利机会数量': all_stock_pool_signal.sum()['win'],
                                       '全市场可盈利机会数量': all_mkt_signal.sum()['win']})
    monthly_opputunity['信号命中率'] = monthly_opputunity['盈利信号数量'] / monthly_opputunity['股票池可盈利机会数量']
    monthly_opputunity['股票池命中率'] = monthly_opputunity['股票池可盈利机会数量'] / monthly_opputunity['全市场可盈利机会数量']




    return daily_signal_stat, daily_signal_win_rate, opputunity,monthly_signal_stat, monthly_signal_win_rate, monthly_opputunity


def main():

    import datetime
    from dataApi.tradeDate import get_pre_trade_date
    start = 20210910
    end = 20211215#get_pre_trade_date(int(datetime.date.today().strftime('%Y%m%d')))

    date_list = get_date_range(start, end)
    date_list.remove(20211124)
    date_list.remove(20211202)

    # daily_signal_stat, daily_signal_win_rate, opputunity,monthly_signal_stat, monthly_signal_win_rate, monthly_opputunity = \
    #     get_signal_stat(date_list,'/data/group/800442/800319/EMExternalPoolTrace/strategy_local_path_TX/')
    daily_signal_stat, daily_signal_win_rate, opputunity, monthly_signal_stat, monthly_signal_win_rate, monthly_opputunity = \
        get_signal_stat(date_list, '/data/user/015664/StrategyBackUp/strategy_local_path3DailyBackup/')


    # corr = pd.DataFrame({'IC':corr,'近五日IC':recent_5_day_corr})

    out_file = f'/data/user/015664/AFuckingTrigger/信号分析Attribution/模型信号分析_{end}_Alpha池信号.xlsx'
    with pd.ExcelWriter(out_file) as writer:
        pd.concat([daily_signal_stat, daily_signal_win_rate, opputunity], axis=1).to_excel(writer, '逐日信号收益命中情况')
        pd.concat([monthly_signal_stat, monthly_signal_win_rate, monthly_opputunity], axis=1).to_excel(writer, '逐月信号收益命中情况')

    writer.close()

    send_file(['015664'], out_file)

main()

