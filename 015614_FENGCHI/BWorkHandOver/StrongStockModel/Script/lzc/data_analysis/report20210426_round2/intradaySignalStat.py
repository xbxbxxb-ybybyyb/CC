# @Time : 2021/4/27 9:32
# @Author : Zhichen Lu
# @File : intradaySignalStat.py
from online_conf import local_config_path, holding_info_path, code_list_path
from dataApi.getData import get_minute_1factor, get_daily_1factor, trans_int2windcode
from dataApi.tradeDate import get_date_range, get_pre_trade_date
import pandas as pd
import numpy as np
from dataApi.sendInfo import send_file

signal_stat_path = '/data/user/015664/AFuckingTrigger/实盘/%d/成交明细及收盘持仓情况%d.xlsx'
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]

start = 20210406
end = 20210714
date_list = get_date_range(start,end)
date_list.remove(20210630)
date_list.remove(202106701)

all_trigger_signal = []
all_stock_pool_signal = []
all_mkt_signal = []

stk_pool_daily_profit = []
daily_trigger_stk = {}
daily_stock_pool_vwap_profit = {}

vwap = get_daily_1factor('vwap')
adj_factor = get_daily_1factor('adjfactor')
vwap_profit = (vwap * adj_factor).pct_change().shift(-1).loc[date_list]
vwap_profit.columns = vwap_profit.columns.map(trans_int2windcode)

for date in date_list:
    daily_signal = pd.read_excel(signal_stat_path % (date, date), sheet_name=None)
    profit_detail, order_detail = daily_signal['收益明细'], daily_signal['委托成交明细']
    profit_detail = profit_detail[profit_detail['类型'] == '当日买入']
    profit_detail['time'], profit_detail['date'] = (profit_detail['buy_signal_time'] % 10000).astype(int), (profit_detail['buy_signal_time'] // 10000).astype(int)
    profit_detail = profit_detail.set_index(['date', 'time', '证券代码'])

    stock_pool = pd.read_pickle(f'{code_list_path}{get_pre_trade_date(date)}.pkl')
    close_adj = get_minute_1factor('close_badj', date, get_pre_trade_date(date, -1))
    close_adj = close_adj.swaplevel(0, 1).loc[bar_list].swaplevel(0, 1)
    ret = close_adj.pct_change(7).shift(-7)
    ret.columns = ret.columns.map(trans_int2windcode)
    ret = ret.loc[[date]].stack()
    stock_pool_ret = ret.swaplevel(0, 2).loc[stock_pool].swaplevel(0, 2)

    profit_detail['未来240分钟收益'] = ret.loc[profit_detail.index]
    all_trigger_signal.append(profit_detail[['累计成交数量', '未来240分钟收益']])
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

# all_stock_pool_signal['rank'] =
# stock_pool_bin = pd.DataFrame({'信号收益':all_stock_pool_signal,'bin':(all_stock_pool_signal.rank(ascending=False)-1)//3360})
# stock_pool_bin['是否触发信号'] = np.nan
# stock_pool_bin.loc[all_trigger_signal.index,'是否触发信号'] = all_trigger_signal['未来240分钟收益']

# signal_ret_stat = stock_pool_bin.groupby('bin').mean()
# signal_ret_stat.columns=['股票池可交易机会平均收益','实际触发信号收益']
# count = stock_pool_bin.groupby('bin').count()
# count.cumsum()/count.sum()
# signal_ret_stat['触发信号数'] = count['是否触发信号']
# signal_ret_stat['触发信号累计占比'] = count['是否触发信号'].cumsum()/count['是否触发信号'].sum()

daily_signal_stat = pd.DataFrame({'信号平均收益率': all_trigger_signal.groupby(level=0).mean()['未来240分钟收益'],

                                  '股票池可交易信号平均收益率': all_stock_pool_signal.groupby(level=0).mean(),
                                  '全市场可交易信号平均收益率': all_mkt_signal.groupby(level=0).mean(),
                                  '信号数量': all_trigger_signal.groupby(level=0).size()
                                  })
daily_signal_stat.loc['全时段'] = pd.Series({'信号平均收益率': all_trigger_signal.mean()['未来240分钟收益'],
                                          '股票池可交易信号平均收益率': all_stock_pool_signal.mean(),
                                          '全市场可交易信号平均收益率': all_mkt_signal.mean(),
                                          '信号数量': all_trigger_signal.shape[0],
                                          })

daily_signal_win_rate = pd.DataFrame({'信号胜率': (all_trigger_signal > 0.0012).groupby(level=0).mean()['未来240分钟收益'],
                                      '股票池可交易信号胜率': (all_stock_pool_signal > 0.0012).groupby(level=0).mean(),
                                      '全市场可交易信号胜率': (all_mkt_signal > 0.0012).groupby(level=0).mean()})
daily_signal_win_rate.loc['全时段'] = pd.Series({'信号胜率': (all_trigger_signal > 0.0012).mean()['未来240分钟收益'],
                                              '股票池可交易信号胜率': (all_stock_pool_signal > 0.0012).mean(),
                                              '全市场可交易信号胜率': (all_mkt_signal > 0.0012).mean()})

opputunity = pd.DataFrame({'盈利信号数量': (all_trigger_signal > 0.0012).groupby(level=0).sum()['未来240分钟收益'],
                           '股票池可盈利机会数量': (all_stock_pool_signal > 0.0012).groupby(level=0).sum(),
                           '全市场可盈利机会数量': (all_mkt_signal > 0.0012).groupby(level=0).sum()})
opputunity.loc['全时段'] = pd.Series({'盈利信号数量': (all_trigger_signal > 0.0012).sum()['未来240分钟收益'],
                                   '股票池可盈利机会数量': (all_stock_pool_signal > 0.0012).sum(),
                                   '全市场可盈利机会数量': (all_mkt_signal > 0.0012).sum()})
opputunity['信号命中率'] = opputunity['盈利信号数量']/opputunity['股票池可盈利机会数量']
opputunity['股票池命中率'] = opputunity['股票池可盈利机会数量']/opputunity['全市场可盈利机会数量']

from dataApi.indName import sw_level2, wind_sw

wind_sw = {wind_sw[x]: x for x in wind_sw}
industry_info = get_daily_1factor('SW2', date_list=[date])
industry_info.columns = industry_info.columns.map(trans_int2windcode)
industry_info = industry_info.loc[date].apply(lambda x: sw_level2[x] if x in sw_level2 else np.nan)
all_trigger_signal = all_trigger_signal.reset_index()
all_trigger_signal['行业'] = all_trigger_signal['证券代码'].apply(lambda x: industry_info[x])
industry_signal_ = all_trigger_signal.groupby(['date', '行业']).mean()['未来240分钟收益'].unstack().T
industry_signal_['所有信号收益'] = all_trigger_signal.groupby('行业').mean()['未来240分钟收益']
industry_signal_['信号数量'] = all_trigger_signal.groupby('行业').size()
industry_signal_ = industry_signal_.reindex(wind_sw.keys())
industry_signal_['行业代码'] = industry_signal_.index.map(lambda x: wind_sw[x])

industry_signal_count = all_trigger_signal.groupby(['date', '行业']).count()['未来240分钟收益'].unstack().T.fillna(0)
industry_signal_count = industry_signal_count.reindex(wind_sw.keys())
industry_signal_count['行业代码'] = industry_signal_count.index.map(lambda x: wind_sw[x])

daily_stat = []

for date in date_list:
    temp = daily_stock_pool_vwap_profit[date]
    stat = pd.DataFrame({'收益均值': temp.groupby('分层').mean()['未来收益'], '触发股票数量': temp[temp['是否触发']].groupby('分层').size()}).T
    stat.index = pd.MultiIndex.from_tuples([(date, x) for x in stat.index])
    daily_stat.append(stat.fillna(0))

daily_stat = pd.concat(daily_stat).fillna(0)
daily_stat.columns = daily_stat.columns.map(lambda x: '收益排名%d~%d' % (int(x) * 50, int(x + 1) * 50))
daily_stat['总计'] = daily_stat.sum(axis=1)
daily_stat = daily_stat.swaplevel(0, 1)
daily_stat.loc['收益均值', '总计'] = np.nan
daily_stat = daily_stat.swaplevel(0, 1)

from dataApi.getData import get_daily_1factor,get_ind_neutral

industry = get_daily_1factor('SW2')
industry.columns = industry.columns.map(trans_int2windcode)
stock_pool_industry = {}
for date in date_list:
    temp_pool = pd.read_pickle(f'/data/group/800442/800319/strategy_local_path/code_list_no688/{get_pre_trade_date(date)}.pkl')
    temp_pool = [trans_int2windcode(x) if isinstance(x,int) else x for x in temp_pool]
    stock_pool_industry[date] = industry.loc[date,temp_pool].apply(lambda x : sw_level2[x]).to_frame().groupby(date).size().astype(int)

stock_pool_industry = pd.DataFrame(stock_pool_industry)

# stock_pool_industry = pd.read_excel('/data/user/015664/AFuckingTrigger/汇报20210426_round2/股票池统计600支.xlsx', sheet_name='行业分布', index_col=0)
top_10_industry_stat = {}

top_10_industry_detail = {}

all_stock_pool_signal = all_stock_pool_signal.reset_index()
all_stock_pool_signal['行业'] = all_stock_pool_signal['level_2'].apply(lambda x: industry_info[x])


for date in date_list:

    top_industry = stock_pool_industry[date].sort_values(ascending=False)[:10].index.tolist()
    top_industry_signal = all_trigger_signal[all_trigger_signal['行业'].isin(top_industry) & all_trigger_signal['date'].eq(date)]
    temp_detail = {}
    temp_detail['行业股票数量(股票池中)'] = stock_pool_industry.loc[top_industry, date]
    temp_detail['当日实际触发信号数量'] = top_industry_signal.groupby('行业').size().reindex(top_industry).fillna(0)
    temp_detail['当日触发信号占比'] = temp_detail['当日实际触发信号数量'].reindex(top_industry).fillna(0) / top_industry_signal.shape[0]
    temp_detail['当日实际触发信号平均收益'] = top_industry_signal.groupby('行业').mean()['未来240分钟收益']
    # if date in stock_pool_industry_ret.columns:
    #     temp_detail['行业股票池涨跌幅'] = stock_pool_industry_ret.loc[top_industry, date]
    temp_detail['股票池该行业所有信号平均收益'] = all_stock_pool_signal[all_stock_pool_signal['行业'].isin(top_industry)&all_stock_pool_signal['date'].eq(date)].groupby('行业').mean()[0]
    temp_detail = pd.DataFrame(temp_detail)
    top_10_industry_detail[date] = temp_detail
    ##################
    day_signal = all_trigger_signal[all_trigger_signal['date'].eq(date)]
    if day_signal.shape[0]==0:
        continue
    top_10_industry_stat[date] = pd.Series({
        'Top10行业触发信号收益均值': top_industry_signal['未来240分钟收益'].mean(),
        'Top10行业触发信号收益中位数': top_industry_signal['未来240分钟收益'].median(),
        'Top10行业触发信号胜率': (top_industry_signal['未来240分钟收益'] > 0.0012).mean(),

        'Top10行业可交易机会收益均值': all_stock_pool_signal[all_stock_pool_signal['行业'].isin(top_industry)&all_stock_pool_signal['date'].eq(date)][0].mean(),
        'Top10行业可交易机会收益收益中位数': all_stock_pool_signal[all_stock_pool_signal['行业'].isin(top_industry)&all_stock_pool_signal['date'].eq(date)][0].median(),
        'Top10行业可交易机会收益胜率': (all_stock_pool_signal[all_stock_pool_signal['行业'].isin(top_industry)&all_stock_pool_signal['date'].eq(date)][0] > 0.0012).mean(),

        'Top10行业触发信号占比': top_industry_signal.shape[0] / day_signal.shape[0],
        'Top10行业触发信号数量': top_industry_signal.shape[0],
        '当日信号数量': day_signal.shape[0],
    })


top_10_industry_detail_df = []
for date in date_list:
    temp = top_10_industry_detail[date].copy().sort_values('股票池该行业所有信号平均收益',ascending=False)
    temp.index = pd.MultiIndex.from_tuples([(date,x) for x in temp.index])
    top_10_industry_detail_df.append(temp)

top_10_industry_detail_df = pd.concat(top_10_industry_detail_df)


out_file = '/data/user/015664/AFuckingTrigger/信号分析/信号分析_含每日行业信号数量_含TOP10行业信号统计.xlsx'
with pd.ExcelWriter(out_file) as writer:
    pd.concat([daily_signal_stat, daily_signal_win_rate, opputunity], axis=1).to_excel(writer, '信号收益命中情况')
    daily_stat.to_excel(writer, '信号分层')
    industry_signal_.to_excel(writer, '按行业统计信号')
    industry_signal_count.to_excel(writer, '行业信号数量')
    pd.DataFrame(top_10_industry_stat).to_excel(writer, 'TOP10行业信号统计')
    top_10_industry_detail_df.to_excel(writer,'TOP10逐日汇总')
    for date in top_10_industry_detail:
        top_10_industry_detail[date].to_excel(writer, str(date))
writer.close()

send_file(['015664'], out_file)

