# @Time : 2020/12/2 11:10
# @Author : Zhichen Lu
# @File : EnsembleMonitorAnalysis.py


import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from StrongStockModel.conf.path_config import root_path
from dataApi.getData import get_daily_1factor
from xquant.factordata import FactorData
s = FactorData()
profit_list, daily_stat_list, signaly_stat_list, cash_occupy_list, daily_buy, daily_holding, daily_profit_list,daily_profit_rate_list = [], [], [], [], [], [], [], []

base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/FactorEvalRev/'  # root_path + 'backtest_result_all_mkt_10bp_cost_revised_framework20201013/'
file_list = ['Linear_XGB_OutSample_DTC_SeperateEnsemble_InSample_UpHolding300_UpBuy100_10bp_cost.xlsx']

# base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/Rev240DTC/'
# file_list = [ 'Linear_XGB_SeperateEnsemble_UpHolding300_UpBuy100_10bp_cost.xlsx']


wind_a = s.get_factor_value('WIND_AIndexWindIndustriesEOD',S_INFO_WINDCODE=['881001.WI'])[['TRADE_DT','S_DQ_CLOSE']].set_index('TRADE_DT')
wind_a = wind_a.sort_index().loc['20151030':'20201030']
wind_a.index = wind_a.index.astype(int)

stock_pool = pd.read_pickle(root_path+'stock_pool_without_limit_up_down.pkl')
close_badj = get_daily_1factor('close_badj',code_list=stock_pool.columns.tolist(),date_list=stock_pool.index.tolist())
close_badj = close_badj.loc[20151030:]
# close_badj.index = pd.to_datetime(close_badj.index.astype(str))

active_1 = (close_badj.pct_change(1).T - wind_a[wind_a.columns[0]].pct_change(1)).T.loc[20160104:].stack(dropna=False)
active_5 = (close_badj.pct_change(5).T - wind_a[wind_a.columns[0]].pct_change(5)).T.loc[20160104:].stack(dropna=False)
active_10 = (close_badj.pct_change(10).T - wind_a[wind_a.columns[0]].pct_change(10)).T.loc[20160104:].stack(dropna=False)
active_20 = (close_badj.pct_change(20).T - wind_a[wind_a.columns[0]].pct_change(20)).T.loc[20160104:].stack(dropna=False)



monthly_pre_active = {}

for file_name in file_list:
    clf_name = file_name.replace('.xlsx', '').replace('_validation','')

    all_data = pd.read_excel(base_path + file_name, sheet_name=None, index_col=0)

    data = all_data['逐笔持仓统计']
    data['id'] = (data['start'] // 10000).astype(str) + '_' + data['stk_id'].astype(str)
    data['id'] = data['id'].apply(lambda x: tuple(map(int, x.split('_'))))
    data['前1日超额'] = data['id'].apply(lambda x: active_1[x])
    data['前5日超额'] = data['id'].apply(lambda x: active_5[x])
    data['前10日超额'] = data['id'].apply(lambda x: active_10[x])
    data['前20日超额'] = data['id'].apply(lambda x: active_20[x])

    pre_active = data[['end', '前1日超额', '前5日超额', '前10日超额', '前20日超额']].set_index('end')
    pre_active.index = pd.to_datetime(pre_active.index.astype(str))
    monthly_pre_active[clf_name] = pre_active.resample('1m').mean()

    data = all_data['每日持仓统计']  # pd.read_excel(root_path + 'backtest_result_all_mkt_10bp_cost/' + file_name, sheet_name='每日持仓统计', index_col=0)
    profit_list.append(data[['累积收益']].rename(columns={'累积收益': clf_name}))
    cash_occupy_list.append(data[['占用资金']].rename(columns={'占用资金': clf_name}))
    daily_profit_list.append(data[['当日收益']].rename(columns={'当日收益': clf_name}))
    daily_profit_rate_list.append(data[['当日收益率']].rename(columns={'当日收益率': clf_name}))

    daily_cout = data[['买入股票数', '卖出股票数']]
    daily_buy.append(daily_cout[['买入股票数']].rename(columns={'买入股票数': clf_name}))
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

    print(clf_name)

monthly_pre_active = pd.Panel(monthly_pre_active)
daily_profit_compare = pd.concat(daily_profit_list,axis=1)
daily_profit_rate_compare = pd.concat(daily_profit_rate_list,axis=1)
daily_profit_compare.index = pd.to_datetime(daily_profit_compare.index.astype(str))
daily_profit_rate_compare.index = pd.to_datetime(daily_profit_rate_compare.index.astype(str))


cash_occupy_compare = pd.concat(cash_occupy_list, axis=1)  # .fillna(0)
cash_occupy_compare.index = pd.to_datetime(cash_occupy_compare.index.astype(str))
daily_stat = pd.concat(daily_stat_list).reset_index().set_index(['index', '模型']).sort_index()
daily_vol = (daily_stat.loc['收益率均值'] / daily_stat.loc['收益率波动']).reset_index()
daily_vol['index'] = '收益均值/收益波动率'
daily_vol = daily_vol.set_index(['index', '模型'])
daily_stat = pd.concat([daily_stat, daily_vol])
signaly_stat = pd.concat(signaly_stat_list).reset_index().set_index(['index', '模型']).sort_index()
daily_holding = pd.concat(daily_holding, axis=1)
daily_holding.index = pd.to_datetime(daily_holding.index.astype(str))
daily_buy = pd.concat(daily_buy, axis=1)
daily_buy.index = pd.to_datetime(daily_buy.index.astype(str))

profit_compare = pd.concat(profit_list, axis=1).fillna(method='pad')
profit_compare['year'] = [x//10000 for x in profit_compare.index]
yearly_drawdown_stat = {}
mdd_info = pd.DataFrame()
for year in list(set(profit_compare['year']))+[-1]:
    if year==-1:
        year = 'all'
        temp_prof_comp = profit_compare.sort_index()
    else:
        temp_prof_comp = profit_compare[profit_compare['year'].eq(year)].sort_index()
    cummax = temp_prof_comp.cummax()
    cum_mdd = ( cummax- temp_prof_comp).drop('year',axis=1)
    mdd_end = cum_mdd.idxmax()
    mdd_start = pd.Series()
    for model_name in mdd_end.index:
        top_val = cummax.loc[mdd_end[model_name],model_name]
        mdd_start[model_name] = cummax[model_name].eq(top_val).idxmax()
    mdd_period = pd.DataFrame({'start':mdd_start,'end':mdd_end}).T
    mdd_period['year'] = year
    mdd_period = mdd_period.reset_index().set_index(['year','index'])
    mdd_info = mdd_info.append(mdd_period)
    cum_mdd.index = pd.to_datetime(cum_mdd.index.astype(str))
    yearly_drawdown_stat[year] = cum_mdd


profit_compare.index = pd.to_datetime(profit_compare.index.astype(str))
profit_compare = profit_compare.drop('year',axis=1)

draw_down_info = pd.concat([yearly_drawdown_stat[x] for x in list(filter(lambda x : isinstance(x,int),list(yearly_drawdown_stat.keys())))])

wind_a = wind_a.loc[20160104:]#s.get_factor_value('WIND_AIndexWindIndustriesEOD',S_INFO_WINDCODE=['881001.WI'])[['TRADE_DT','S_DQ_CLOSE']].set_index('TRADE_DT').loc['20160104':]
wind_a.index = wind_a.index.astype(str)
kcb_szzs = s.get_factor_value('Basic_factor',['000001.SH','399006.SZ','399001.SZ','000300.SH','000905.SH'],factor_names=['close'],mddate=wind_a.index.tolist())
kcb_szzs =kcb_szzs.reset_index().pivot_table(index='mddate',columns='stock',values='close').sort_index()

indexes = pd.concat([wind_a,kcb_szzs],axis=1).rename(columns=
                        {'S_DQ_CLOSE':'万德全A','000001.SH':'上证指数','399006.SZ':'创业板指',
                         '399001.SZ':'深证成指','000300.SH':'沪深300','000905.SH':'中证500'}).sort_index()
indexes.index = pd.to_datetime(indexes.index)
indexes = indexes.loc[profit_compare.index]

index_daily_pct = indexes.pct_change()
index_daily_stat = {}
index_daily_stat['日胜率'] = pd.concat([(index_daily_pct>0).resample('1y').mean(),pd.DataFrame({'全时段':(index_daily_pct>0).mean()}).T])
index_daily_stat['收益率盈亏比'] = -1*pd.concat([index_daily_pct[index_daily_pct>0].resample('1y').mean()/index_daily_pct[index_daily_pct<0].resample('1y').mean(),
                                   pd.DataFrame({'全时段':index_daily_pct[index_daily_pct>0].mean()/index_daily_pct[index_daily_pct<0].mean()}).T])
index_daily_stat['收益率均值'] = pd.concat([index_daily_pct.resample('1y').mean(),pd.DataFrame({'全时段':index_daily_pct.mean()}).T])
index_daily_stat['收益率波动'] = pd.concat([index_daily_pct.resample('1y').std(),pd.DataFrame({'全时段':index_daily_pct.std()}).T])
index_daily_stat['收益均值/收益波动率'] = index_daily_stat['收益率均值']/index_daily_stat['收益率波动']

index_daily_stat_df = []
for each in index_daily_stat:
    temp = index_daily_stat[each].T
    temp.columns = [int(x.strftime('%Y')) for x in temp.columns[:-1]] + [temp.columns[-1]]
    temp['indicator'] = each
    temp = temp.reset_index().set_index(['indicator','index'])
    index_daily_stat_df.append(temp)
index_daily_stat_df = pd.concat(index_daily_stat_df)
# check = daily_stat.append(index_daily_stat_df).sort_index()
# daily_stat = daily_stat.append(index_daily_stat_df).sort_index()

index_monthly_stat = indexes.resample('1m').last() / indexes.resample('1m').first() - 1
monthly_stat = {}
monthly_stat['月度收益'] = pd.concat([profit_compare.resample('1m').last() - profit_compare.resample('1m').first(),
                                  index_monthly_stat], axis=1, join='inner')
monthly_stat['月度收益率(日收益累加比占资均值)'] = (profit_compare.resample('1m').last() - profit_compare.resample('1m').first())/cash_occupy_compare.resample('1m').mean()
monthly_stat['月度收益率(日收益累加比占资均值)'] = pd.concat([monthly_stat['月度收益率(日收益累加比占资均值)'],
                                               index_monthly_stat], axis=1, join='inner')
monthly_stat['月度收益率(日收益均值比占资均值)'] = daily_profit_compare.resample('1m').mean()/cash_occupy_compare.resample('1m').mean()
monthly_stat['月度买入信号数'] = daily_buy.resample('1m').sum()

# cum_MDD = (profit_compare.cummax() - profit_compare).cummax()
# check =

indexes = indexes.reindex(yearly_drawdown_stat['all'].index)
# check =
# pd.to_pickle([profit_list,daily_stat_list,signaly_stat_list],'/data/user/015664/AFuckingTrigger/XGB回归滚动阈值结果汇总.pkl')
with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/年终汇报/样本外v2.xlsx') as writer:
    pd.concat([profit_compare,indexes],axis=1).to_excel(writer, sheet_name='累计收益')
    daily_profit_compare.to_excel(writer, sheet_name='单日收益')
    daily_profit_rate_compare.to_excel(writer, sheet_name='单日收益率')
    ###############
    mdd_info.to_excel(writer, sheet_name='最大回撤区间')
    draw_down_info.to_excel(writer, sheet_name='累计最大回撤(逐年)')
    pd.concat([yearly_drawdown_stat['all'],indexes/indexes.loc[indexes.index[0]]],axis=1).to_excel(writer, sheet_name='累计最大回撤(全周期)')
    for each in monthly_stat:
        monthly_stat[each].to_excel(writer, sheet_name=each)
    monthly_stat['月度收益'].corr().to_excel(writer, sheet_name='模型-指数间月度收益相关性')
    pd.concat([monthly_stat['月度收益率(日收益均值比占资均值)'],
               index_monthly_stat], axis=1, join='inner').corr().to_excel(writer, sheet_name='模型-指数间月度收益率(日收益均值比占资均值)相关性')
    monthly_stat['月度收益率(日收益累加比占资均值)'].corr().to_excel(writer, sheet_name='模型-指数间月度收益率(日收益累加比占资均值)相关性')
    for each in monthly_pre_active.minor_axis:
        monthly_pre_active.loc[:,:,each].to_excel(writer, sheet_name=each)
    ###############
    cash_occupy_compare.to_excel(writer, sheet_name='占用资金')
    daily_holding.to_excel(writer, sheet_name='持仓股票数')
    daily_buy.to_excel(writer, sheet_name='每日触发数量')
    daily_stat.reset_index().set_index(['index', '模型']).sort_index().T.to_excel(writer, sheet_name='日收益综合统计')
    signaly_stat.reset_index().set_index(['index', '模型']).sort_index().T.to_excel(writer, sheet_name='按信号综合统计')

writer.close()

from xquant.xqutils.helper import link
lm = link.LinkMessage()
lm.sendMessage("结果统计结束")

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
