# @Time : 2020/9/18 9:25
# @Author : Zhichen Lu
# @File : backtest_result_analysis.py


import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from StrongStockModel.conf.path_config import root_path
from dataApi.getData import get_daily_1factor
from dataApi.tradeDate import get_pre_trade_date
from xquant.factordata import FactorData
import numpy as np

s = FactorData()
net_Value_list, daily_stat_list, signaly_stat_list, cash_occupy_list, daily_buy, daily_holding, daily_profit_rate_list = [], [], [], [], [], [], []
profit_list = []
account_cap = []
holding_time_count = []
# base_path = '/data/user/015664/AFuckingTrigger/不限制买入卖出信号(老版本)/'#'/data/user/015664/AFuckingTrigger/限制买入和持仓/FactorEvalRev/'
# base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEra/'
# file_list = ['XGB_lightGBM_CatBoostAlphaTriggerPoolV3Top600_real600_deal_ratio_0.1_per_ratio_0.0050_threshold_0.05VolConsider_UpBuy100_10bp_cost.xlsx']

# base_path = '/data/user/015664/AFuckingTrigger/DataForPaperWork/BacTestRes/'

base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/Upgrade/'
# file_list = list(filter(lambda x: x.startswith('XGB') and 'Out' not in x, os.listdir(base_path)))
file_list = sorted(list(filter(lambda x: x.endswith('xlsx'), os.listdir(base_path))))
file_list = [f'{x}.xlsx' for x in ['OLS_XGB200Top200',
 'OLS_XGB200Top300',
 'OLS_XGB200Top400',
 'OLS_XGB200Top450',
 'OLS_XGB200Top500',
 'OLS_XGB200Top600',
 'OLS_XGB200Top700',
 'OLS_XGB200_auctionTop200',
 'OLS_XGB200_auctionTop300',
 'OLS_XGB200_auctionTop400',
 'OLS_XGB200_auctionTop450',
 'OLS_XGB200_auctionTop500',
 'OLS_XGB200_auctionTop600',
 'OLS_XGB200_auctionTop700',
 'OLS_T3Top200',
 'OLS_T3Top300',
 'OLS_T3Top400',
 'OLS_T3Top450',
 'OLS_T3Top500',
 'OLS_T3Top600',
 'OLS_T3Top700',
 'XGB_OLS_style_ex20Top200',
 'XGB_OLS_style_ex20Top300',
 'XGB_OLS_style_ex20Top400',
 'XGB_OLS_style_ex20Top450',
 'XGB_OLS_style_ex20Top500',
 'XGB_OLS_style_ex20Top600',
 'XGB_OLS_style_ex20Top700']]

# list(filter(lambda x : not os.path.exists(f'{base_path}{x}'),file_list))

wind_a = s.get_factor_value('WIND_AIndexWindIndustriesEOD', S_INFO_WINDCODE=['881001.WI'])[['TRADE_DT', 'S_DQ_CLOSE']].set_index('TRADE_DT')
wind_a = wind_a.sort_index().loc['20151231':]
wind_a.index = wind_a.index.astype(int)
# sz50 = s.get_factor_value('WIND_AIndexWindIndustriesEOD', S_INFO_WINDCODE=['000016.SH'])[['TRADE_DT', 'S_DQ_CLOSE']].set_index('TRADE_DT')

monthly_pre_active = {}

for file_name in file_list:
    clf_name = file_name.replace('.xlsx','')
    # print(clf_name)
    all_data = pd.read_excel(base_path + file_name, sheet_name=None, index_col=0)

    # data = all_data['逐笔持仓统计']
    # data['id'] = (data['start'] // 10000).astype(str) + '_' + data['stk_id'].astype(str)
    # data['id'] = data['id'].apply(lambda x: tuple(map(int, x.split('_'))))
    # data['前1日超额'] = data['id'].apply(lambda x: active_1[x])
    # data['前5日超额'] = data['id'].apply(lambda x: active_5[x])
    # data['前10日超额'] = data['id'].apply(lambda x: active_10[x])
    # data['前20日超额'] = data['id'].apply(lambda x: active_20[x])
    #
    # pre_active = data[['end', '前1日超额', '前5日超额', '前10日超额', '前20日超额']].set_index('end')
    # pre_active.index = pd.to_datetime(pre_active.index.astype(str))
    # monthly_pre_active[clf_name] = pre_active.resample('1m').mean()

    data = all_data['每日持仓统计']  # pd.read_excel(root_path + 'backtest_result_all_mkt_10bp_cost/' + file_name, sheet_name='每日持仓统计', index_col=0)
    net_Value_list.append(data[['账户净值']].rename(columns={'账户净值': clf_name}))
    cash_occupy_list.append(pd.DataFrame({clf_name: data['收盘持仓市值'] / data['收盘账户市值'].replace('pad', np.nan).fillna(method='pad')}))
    account_cap.append(pd.DataFrame({clf_name: data['收盘持仓市值']}))
    # daily_profit_list.append(data[['当日收益']].rename(columns={'当日收益': clf_name}))
    daily_profit_rate_list.append(data[['当日收益率']].rename(columns={'当日收益率': clf_name}))
    profit_list.append(data[['累积收益']].rename(columns={'累积收益': clf_name}))

    daily_cout = data[['买入股票数', '卖出股票数']]
    daily_buy.append(daily_cout[['买入股票数']].rename(columns={'买入股票数': clf_name}))
    if '持仓股票数' in data.columns:
        daily_holding.append(pd.DataFrame({clf_name: data['持仓股票数']}))
    daily_holding.append(pd.DataFrame({clf_name: (daily_cout['买入股票数'] - daily_cout['卖出股票数']).cumsum()}))
    daily_cout['year'] = [x // 10000 for x in daily_cout.index]
    yealy_stat = daily_cout.groupby('year').mean()
    yealy_stat.loc['全时段'] = daily_cout.mean()
    yealy_stat.columns = ['平均每天买入股票数', '平均每天卖出股票数']

    data = all_data['持仓综合统计']  # pd.read_excel(base_path + file_name, sheet_name='持仓综合统计', index_col=0)
    data = data.append(yealy_stat.T)
    data['模型'] = clf_name
    daily_stat_list.append(data)

    data = all_data['逐笔持仓综合统计']  # pd.read_excel(base_path + file_name, sheet_name='逐笔持仓综合统计', index_col=0)
    data['模型'] = clf_name
    signaly_stat_list.append(data)

    data = all_data['逐笔持仓统计']
    data['year'] = data['end'].apply(lambda x: int(str(x)[:4]))
    holding_time = data[['year', 'holding_minutes']].groupby('year').mean()
    holding_time.loc['全时段'] = data['holding_minutes'].mean()
    holding_time_count.append(holding_time)
    print(clf_name)

holding_time_count = pd.concat(holding_time_count, axis=1)

monthly_pre_active = pd.Panel(monthly_pre_active)
daily_profit_rate_compare = pd.concat(daily_profit_rate_list, axis=1)
daily_profit_rate_compare.index = pd.to_datetime(daily_profit_rate_compare.index.astype(str))

cash_occupy_compare = pd.concat(cash_occupy_list, axis=1)  # .fillna(0)
cash_occupy_compare.index = pd.to_datetime(cash_occupy_compare.index.astype(str))
daily_stat = pd.concat(daily_stat_list).reset_index().set_index(['index', '模型']).sort_index()
# daily_vol = (daily_stat.loc['收益率均值']* (244**0.5) / daily_stat.loc['收益率波动']).reset_index() #
# daily_vol['index'] = '年化夏普'
# daily_vol = daily_vol.set_index(['index', '模型'])
# daily_stat = pd.concat([daily_stat, daily_vol])
signaly_stat = pd.concat(signaly_stat_list).reset_index().set_index(['index', '模型']).sort_index()
daily_holding = pd.concat(daily_holding, axis=1)
daily_holding.index = pd.to_datetime(daily_holding.index.astype(str))
daily_buy = pd.concat(daily_buy, axis=1)
daily_buy.index = pd.to_datetime(daily_buy.index.astype(str))

net_compare = pd.concat(net_Value_list, axis=1).replace(0, np.nan).fillna(method='pad')
net_compare['year'] = [x // 10000 for x in net_compare.index]
yearly_drawdown_stat = {}
mdd_info = pd.DataFrame()
for year in list(set(net_compare['year'])) + [-1]:
    if year == -1:
        year = 'all'
        temp_prof_comp = net_compare.sort_index()
    else:
        temp_prof_comp = net_compare[net_compare['year'].eq(year)].sort_index()
    cummax = temp_prof_comp.cummax()
    cum_mdd = ((cummax - temp_prof_comp) / temp_prof_comp).drop('year', axis=1)
    mdd_end = cum_mdd.idxmax()
    mdd_start = pd.Series()
    for model_name in mdd_end.index:
        top_val = cummax.loc[mdd_end[model_name], model_name]
        mdd_start[model_name] = cummax[model_name].eq(top_val).idxmax()
    mdd_period = pd.DataFrame({'start': mdd_start, 'end': mdd_end}).T
    mdd_period['year'] = year
    mdd_period = mdd_period.reset_index().set_index(['year', 'index'])
    mdd_info = mdd_info.append(mdd_period)
    cum_mdd.index = pd.to_datetime(cum_mdd.index.astype(str))
    yearly_drawdown_stat[year] = cum_mdd

pre_date = get_pre_trade_date(net_compare.index[0])
net_compare = net_compare.reindex([pre_date] + net_compare.index.tolist())
net_compare.loc[pre_date, :] = 1
net_compare.index = pd.to_datetime(net_compare.index.astype(str))
net_compare = net_compare.drop('year', axis=1)

draw_down_info = pd.concat([yearly_drawdown_stat[x] for x in list(filter(lambda x: isinstance(x, int), list(yearly_drawdown_stat.keys())))])

wind_a = wind_a.loc[pre_date:]  # s.get_factor_value('WIND_AIndexWindIndustriesEOD',S_INFO_WINDCODE=['881001.WI'])[['TRADE_DT','S_DQ_CLOSE']].set_index('TRADE_DT').loc['20160104':]
wind_a.index = wind_a.index.astype(str)
kcb_szzs = s.get_factor_value('Basic_factor', ['000001.SH', '399006.SZ', '399001.SZ', '000300.SH', '000905.SH', '000016.SH', '000852.SH'], factor_names=['close'],
                              mddate=wind_a.index.tolist())
kcb_szzs = kcb_szzs.reset_index().pivot_table(index='mddate', columns='stock', values='close').sort_index()

# kcb_szzs = s.get_factor_value('Basic_factor', ['000016.SH','000852.SH'], factor_names=['close'], mddate=wind_a.index.tolist())

indexes = pd.concat([wind_a, kcb_szzs], axis=1).rename(columns=
                                                       {'S_DQ_CLOSE': '万德全A', '000001.SH': '上证指数', '399006.SZ': '创业板指',
                                                        '399001.SZ': '深证成指', '000300.SH': '沪深300', '000905.SH': '中证500',
                                                        '000016.SH': '上证50', '000852.SH': '中证1000'}).sort_index()
indexes.index = pd.to_datetime(indexes.index)

indexes = indexes.loc[net_compare.index]

index_daily_pct = indexes.pct_change()[1:]
index_daily_stat = {}
index_daily_stat['日胜率'] = pd.concat([(index_daily_pct > 0).resample('1y').mean(), pd.DataFrame({'全时段': (index_daily_pct > 0).mean()}).T])
index_daily_stat['收益率盈亏比'] = -1 * pd.concat([index_daily_pct[index_daily_pct > 0].resample('1y').mean() / index_daily_pct[index_daily_pct < 0].resample('1y').mean(),
                                             pd.DataFrame({'全时段': index_daily_pct[index_daily_pct > 0].mean() / index_daily_pct[index_daily_pct < 0].mean()}).T])
index_daily_stat['收益率均值'] = pd.concat([index_daily_pct.resample('1y').mean(), pd.DataFrame({'全时段': index_daily_pct.mean()}).T])
index_daily_stat['收益率波动'] = pd.concat([index_daily_pct.resample('1y').std(), pd.DataFrame({'全时段': index_daily_pct.std()}).T])
index_daily_stat['年化夏普'] = (244 ** 0.5) * index_daily_stat['收益率均值'] / index_daily_stat['收益率波动']

index_daily_stat_df = []
for each in index_daily_stat:
    temp = index_daily_stat[each].T
    temp.columns = [int(x.strftime('%Y')) for x in temp.columns[:-1]] + [temp.columns[-1]]
    temp['indicator'] = each
    temp = temp.reset_index().set_index(['indicator', 'index'])
    index_daily_stat_df.append(temp)
index_daily_stat_df = pd.concat(index_daily_stat_df)
check = daily_stat.append(index_daily_stat_df).sort_index()
daily_stat = daily_stat.append(index_daily_stat_df).sort_index()

index_monthly_stat = indexes[1:].resample('1m').last() / indexes[1:].resample('1m').first() - 1
monthly_stat = {}
monthly_stat['月度收益率'] = pd.concat([net_compare[1:].resample('1m').last() / net_compare[1:].resample('1m').first() - 1,
                                   index_monthly_stat], axis=1, join='inner')
monthly_stat['月度买入信号数'] = daily_buy.resample('1m').sum()
cum_profit = pd.concat(profit_list, axis=1)
cum_profit.index = pd.to_datetime(cum_profit.index.astype(str))
account_cap = pd.concat(account_cap, axis=1)
account_cap.index = pd.to_datetime(account_cap.index.astype(str))

net_compare = pd.concat([net_compare, indexes / indexes.loc[indexes.index[0]]], axis=1)
indexes = indexes.reindex(yearly_drawdown_stat['all'].index)
# pd.to_pickle([profit_list,daily_stat_list,signaly_stat_list],'/data/user/015664/AFuckingTrigger/XGB回归滚动阈值结果汇总.pkl')
# with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/剔除未来信息因子后-不同模型集成-全市场活跃股票池对比(含吴雨璘新添加的两个维度模型).xlsx') as writer:


# send_file(['015664'],f'{base_path}/对比大小盘表现与策略收益情况.xlsx')

# net_compare['占资'] = cash_occupy_compare
# net_compare['高占资'] = cash_occupy_compare > 0.8
# for i in range(3, 8):
#     net_compare['近%d日高占资日期数' % i] = net_compare['高占资'].rolling(i).sum()
# net_compare.to_excel(f'{base_path}/高占资统计.xlsx')
# send_file(['015664'], f'{base_path}/高占资统计.xlsx')

all_file = f'{base_path}/股票池对比20211229.xlsx'
with pd.ExcelWriter(all_file) as writer:
    net_compare.to_excel(writer, sheet_name='账户净值对比')
    daily_stat.reset_index().set_index(['index', '模型']).sort_index().to_excel(writer, sheet_name='日收益综合统计')
    signaly_stat.reset_index().set_index(['index', '模型']).sort_index().to_excel(writer, sheet_name='按信号综合统计')
    cum_profit.sort_index(axis=1).replace(0, np.nan).fillna(method='pad').to_excel(writer, sheet_name='账面累积收益')
    cash_occupy_compare.to_excel(writer, sheet_name='占用资金')
    daily_holding.to_excel(writer, sheet_name='持仓股票数')
    daily_buy.to_excel(writer, sheet_name='每日触发数量')

    # daily_buy_stat.to_excel(writer, sheet_name='触发数量分布统计')
    holding_time_count.to_excel(writer, sheet_name='持仓时间统计')
    account_cap.sort_index(axis=1).to_excel(writer, sheet_name='持仓市值')
    daily_profit_rate_compare.to_excel(writer, sheet_name='单日收益率')
    ###############
    mdd_info.to_excel(writer, sheet_name='最大回撤区间')
    draw_down_info.to_excel(writer, sheet_name='累计最大回撤(逐年)')
    pd.concat([yearly_drawdown_stat['all'], indexes / indexes.loc[indexes.index[0]]], axis=1).to_excel(writer, sheet_name='累计最大回撤(全周期)')
    for each in monthly_stat:
        monthly_stat[each].to_excel(writer, sheet_name=each)
    monthly_stat['月度收益率'].corr().to_excel(writer, sheet_name='模型-指数间月度收益相关性')
    for each in monthly_pre_active.minor_axis:
        monthly_pre_active.loc[:, :, each].to_excel(writer, sheet_name=each)
    ###############

writer.close()
# (indexes.resample('1y').last()/indexes.resample('1y').first() - 1).to_excel('/data/user/015664/AFuckingTrigger/基于初始资金考虑成交_样本内指数_v3.xlsx')

from dataApi.sendInfo import send_file

send_file(['015664'], all_file)

"""

# profit_compare.plot(figsize=(20,14))
# plt.xticks(fontsize=18)
# plt.yticks(fontsize=18)
# plt.legend(fontsize=25)
# plt.savefig('/data/user/015664/AFuckingTrigger/XGB回归验证集真实涨幅分位数阈值结果汇总(按IC筛因子).png')
# plt.show()
# pred = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl')
# val_pred = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40_val_pred/20151225.pkl')
# def clear(path):
#     file_list = os.listdir(path)
#     for each in file_list:
#         os.remove(path+each)
# N = 60
# factor_out_path = root_path + 'processed_factor_by_factor/ts_maxmin/'#%N
# clear(factor_out_path)

import pandas as pd
from dataApi.stockList import clean_stock_list

stock_pool = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl').shift(1).rank(
    ascending=False, axis=1) < 600
param = dict(no_ST=False, least_live_days=1, no_pause=False, least_recover_days=0,
             no_pause_limit=0, no_pause_stats_days=0, no_limit_up=False, no_limit_down=False,
             other_limit=None, start_date=stock_pool.index[0], end_date=stock_pool.index[-1], trade_mode=False, )

# pool_50 = clean_stock_list('SZ50', **param)
pool_300 = clean_stock_list('HS300', **param)
# pool_500 = clean_stock_list('ZZ500', **param)
# pool_1000 = clean_stock_list('ZZ1000', **param)
# pool_1800 = clean_stock_list('COMMON', **param)

net_compare = net_compare[['只用FIX(原股票池)', '只用FIX(300涨小盘跌替换300)', '只用FIX(300涨小盘跌前一天替换300)', '上证50', '沪深300', '中证1000', '创业板指']]
ret_compare = net_compare.pct_change().rename(columns={x: x + ' 收益' for x in net_compare.columns})
quantile_90 = ret_compare.rolling(20).apply(lambda x: x[-1] > np.nanquantile(x, 0.9)).rename(columns={x: x.replace('收益', '收益大于90分位数') for x in ret_compare.columns})
quantile_10 = ret_compare.rolling(20).apply(lambda x: x[-1] < np.nanquantile(x, 0.1)).rename(columns={x: x.replace('收益', '收益小于10分位数') for x in ret_compare.columns})

stat = {}

for each in quantile_10.columns[1:]:
    stat[each] = ret_compare[quantile_10[each] > 0.5]
for each in quantile_90.columns[1:]:
    stat[each] = ret_compare[quantile_90[each] > 0.5]

stat['50涨_1000跌'] = ret_compare[(ret_compare['上证50 收益'] > 0) & (ret_compare['中证1000 收益'] < 0)]
stat['300涨_1000跌'] = ret_compare[(ret_compare['沪深300 收益'] > 0) & (ret_compare['中证1000 收益'] < 0)]
stat['50涨_创业板跌'] = ret_compare[(ret_compare['上证50 收益'] > 0) & (ret_compare['创业板指 收益'] < 0)]
stat['300涨_创业板跌'] = ret_compare[(ret_compare['沪深300 收益'] > 0) & (ret_compare['创业板指 收益'] < 0)]

selected = ((ret_compare['沪深300 收益'] > 0) & (ret_compare['中证1000 收益'] < 0)) | ((ret_compare['沪深300 收益'] > 0) & (ret_compare['创业板指 收益'] < 0))
selected.index = selected.index.map(lambda x: int(x.strftime('%Y%m%d')))
selected = selected.loc[:stock_pool.index[-1]]
selected.index = [get_pre_trade_date(x) for x in selected.index]

stock_pool.loc[selected[selected].index] = pool_300.shift(1).loc[selected[selected].index].reindex(stock_pool.columns, axis=1).fillna(False)
stock_pool.shift(-1).to_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50_PreDayReplace300.pkl')

stat['50跌_1000涨'] = ret_compare[(ret_compare['上证50 收益'] < 0) & (ret_compare['中证1000 收益'] > 0)]
stat['300跌_1000涨'] = ret_compare[(ret_compare['沪深300 收益'] < 0) & (ret_compare['中证1000 收益'] > 0)]
stat['50跌_创业板涨'] = ret_compare[(ret_compare['上证50 收益'] < 0) & (ret_compare['创业板指 收益'] > 0)]
stat['300跌_创业板涨'] = ret_compare[(ret_compare['沪深300 收益'] < 0) & (ret_compare['创业板指 收益'] > 0)]

outine = pd.DataFrame({x: stat[x].mean() for x in stat}).T
outine['日期数'] = pd.Series({x: stat[x].shape[0] for x in stat})
win_rate = pd.DataFrame({x: (stat[x] > 0).mean() for x in stat}).T
win_rate.columns = win_rate.columns.map(lambda x: x + '_日胜率')
outine = pd.concat([outine, win_rate], axis=1)
with pd.ExcelWriter(f'{base_path}/替换300成分股后_对比大小盘表现与策略收益情况.xlsx') as writer:
    # net_compare.to_excel(writer,sheet_name='总揽')
    # net_compare[net_compare['上证50 收益分位数']>0.9].to_excel(writer,sheet_name='上证50 前后10%分位数')
    outine.to_excel(writer, sheet_name='收益均值总揽')
    for each in stat:
        stat[each].to_excel(writer, sheet_name=each)

writer.close()
send_file(['015664'], f'{base_path}/替换300成分股后_对比大小盘表现与策略收益情况.xlsx')
"""

"""
import numpy as np

period_list = [(20160301,20161201),(20160104,20160128),(20160225,20160229),(20161202,20161212),
                  (20170117,20170316),(20170512,20171113),(20170111,20170116),(20170414,20170510),(20180102,20181227)]

period_list = [(20190201,20190404),(20190507,20191231),(20190422,20190506), (20200203,20200225),
                (20200630,20200713),(20200324,20200629),  (20200714,20201029),(20200226,20200323)]
res = []
for tu in period_list:
    start,end = tu
    part = net_compare.loc[str(start):str(end)].T[:2].T
    stat = pd.DataFrame()
    stat['区间收益'] = part.loc[part.index[-1]]/part.loc[part.index[0]] - 1
    temp_draw_down = (part.cummax()/part - 1)
    stat['区间最大回撤'] = temp_draw_down.max()
    #如果对比多个策略需要改！
    stat['区间资金平均占用比例'] = cash_occupy_compare[cash_occupy_compare.columns[0]].loc[str(start):str(end)].mean()
    stat['最大回撤起始日'] = np.nan
    stat['最大回撤截止日'] = (part.cummax()/part - 1).idxmax().apply(lambda x : x.strftime('%Y%m%d'))
    for each in stat.index:
        draw_end = stat['最大回撤截止日'][each]
        stat.loc[each,'最大回撤起始日'] = (part[each].loc[:draw_end]/part[each][draw_end]-1).idxmax().strftime('%Y%m%d')
    stat = stat.rename(index={stat.index[0]:'策略'})
    stat['统计区间'] = '%d-%d'%(start,end)
    stat = stat.reset_index().set_index(['统计区间','index'])
    res.append(stat)

res_df = pd.concat(res)
res_df.to_excel('/data/user/015664/AFuckingTrigger/基于初始资金考虑成交_样本外区间统计.xlsx')
"""
