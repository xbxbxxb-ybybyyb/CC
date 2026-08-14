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
from dataApi.sendInfo import send_file
s = FactorData()
net_Value_list, daily_stat_list, signaly_stat_list, cash_occupy_list, daily_buy, daily_holding, daily_profit_rate_list = [], [], [], [], [], [], []
profit_list = []
account_cap = []
holding_time_count = []
# base_path = '/data/user/015664/AFuckingTrigger/不限制买入卖出信号(老版本)/'#'/data/user/015664/AFuckingTrigger/限制买入和持仓/FactorEvalRev/'
# base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEra/'
# file_list = ['XGB_lightGBM_CatBoostAlphaTriggerPoolV3Top600_real600_deal_ratio_0.1_per_ratio_0.0050_threshold_0.05VolConsider_UpBuy100_10bp_cost.xlsx']

base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityOutSample/'
# file_list = ['XGB_Cat_Light_OnlineTestOutSampleAlphaTriggerPoolV3Top600_real600_deal_ratio_0.1_per_ratio_0.0050_UpBuy100_10bp_cost.xlsx']
file_list = os.listdir(base_path)

file_list = list(filter(lambda x : '.xlsx' in x and x.startswith('XGB'),file_list))

num_str = [str(x) for x in range(10)] + ['.']
para = {'Top':{},
        'deal_ratio':{},
        'per_ratio':{},
        'threshold':{},
}

for p in para:
    for f in file_list:
        if p =='Top':
            print(1)
        start = 0
        while f[start] not in num_str:
            sub_f = f[start:]
            start += sub_f.index(p)+len(p)
            if f[start]=='_':
                start+=1
        not_number = [x in num_str for x in f[start:]]
        end = start + not_number.index(False)
        if f[start:end][-1]=='.':
            end-=1
        para[p][f] = eval(f[start:end])

para = pd.DataFrame(para)
condition = {'per_ratio':[0.02],
             'threshold':[0.04]}
file_list = para.query('per_ratio in [0.02] and threshold in [0.04]').index.tolist()
file_list = file_list + para.query('per_ratio in [0.005] and threshold in [0.05] and Top in [600]').index.tolist()

# file_list = [ 'XGB_Linear_DTC_deal_ratio_0.1_per_ratio_0.0050VolConsiderMultiTrigger_UpBuy100_10bp_cost.xlsx',
#               'XGB_Linear_DTCOnlineTest_deal_ratio_0.1_per_ratio_0.0050VolConsider_UpBuy100_10bp_cost.xlsx']
# file_list=['XGB_Linear_DTC_OutSample_deal_ratio_0.1_per_ratio_0.0050VolConsider_UpBuy100_10bp_cost.xlsx']

wind_a = s.get_factor_value('WIND_AIndexWindIndustriesEOD',S_INFO_WINDCODE=['881001.WI'])[['TRADE_DT','S_DQ_CLOSE']].set_index('TRADE_DT')
wind_a = wind_a.sort_index().loc['20151231':]
wind_a.index = wind_a.index.astype(int)

"""
stock_pool = pd.read_pickle(root_path+'stock_pool_without_limit_up_down.pkl')
close_badj = get_daily_1factor('close_badj',code_list=stock_pool.columns.tolist(),date_list=stock_pool.index.tolist())
close_badj = close_badj.loc[20151030:]

active_1 = (close_badj.pct_change(1).T - wind_a[wind_a.columns[0]].pct_change(1)).T.loc[20160104:].stack(dropna=False)
active_5 = (close_badj.pct_change(5).T - wind_a[wind_a.columns[0]].pct_change(5)).T.loc[20160104:].stack(dropna=False)
active_10 = (close_badj.pct_change(10).T - wind_a[wind_a.columns[0]].pct_change(10)).T.loc[20160104:].stack(dropna=False)
active_20 = (close_badj.pct_change(20).T - wind_a[wind_a.columns[0]].pct_change(20)).T.loc[20160104:].stack(dropna=False)

"""


monthly_pre_active = {}

for file_name in file_list:
    # if 'XGB'in file_name:
    #     clf_name = 'XGB_LightGBM'#file_name.replace('XGB_Light_OnlineTestOutSample20210224','XGB_LightGBM').replace('Top600_deal_ratio_0.1_per_ratio_0.0050VolConsiderOnlineLimit_UpBuy100_10bp_cost.xlsx','')
    # else:
    #     clf_name = 'HXSignal20210107_5min'
    # clf_name = file_name.replace('XGB_lightGBM_CatBoostOutSampleAlphaTriggerPoolV3Top600_real600_deal_ratio_0.1_',
    #                              '')
    # clf_name = clf_name.replace('.xlsx','')

    pool_num = para.loc[file_name, 'Top']
    per_ratio = para.loc[file_name, 'per_ratio']
    threshold = para.loc[file_name, 'threshold']
    clf_name = f'股票池_{pool_num}_委托占比{round(per_ratio * 100, 1)}%_阈值{int(threshold * 100)}%'

    all_data = pd.read_excel(base_path + file_name, sheet_name=None, index_col=0)

    data = all_data['每日持仓统计']  # pd.read_excel(root_path + 'backtest_result_all_mkt_10bp_cost/' + file_name, sheet_name='每日持仓统计', index_col=0)
    net_Value_list.append(data[['账户净值']].rename(columns={'账户净值': clf_name}))
    cash_occupy_list.append(pd.DataFrame({clf_name:data['收盘持仓市值']/data['收盘账户市值'].replace('pad',np.nan).fillna(method='pad')}))
    account_cap.append(pd.DataFrame({clf_name:data['收盘持仓市值']}))
    # daily_profit_list.append(data[['当日收益']].rename(columns={'当日收益': clf_name}))
    daily_profit_rate_list.append(data[['当日收益率']].rename(columns={'当日收益率': clf_name}))
    profit_list.append(data[['累积收益']].rename(columns={'累积收益': clf_name}))

    daily_cout = data[['买入股票数', '卖出股票数']]
    daily_buy.append(daily_cout[['买入股票数']].rename(columns={'买入股票数': clf_name}))
    if '持仓股票数' in data.columns:
        daily_holding.append(pd.DataFrame({clf_name:data['持仓股票数']}))
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

    data= all_data['逐笔持仓统计']
    data['year'] = data['end'].apply(lambda x : int(str(x)[:4]))
    holding_time = data[['year','holding_minutes']].groupby('year').mean()
    holding_time.loc['全时段'] = data['holding_minutes'].mean()
    holding_time_count.append(holding_time)
    print(clf_name)

holding_time_count = pd.concat(holding_time_count,axis=1)

monthly_pre_active = pd.Panel(monthly_pre_active)
daily_profit_rate_compare = pd.concat(daily_profit_rate_list,axis=1)
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
###########

#
# daily_buy_stat = daily_buy.resample('1y').mean()
# daily_buy_stat.loc['全时段'] = daily_buy.mean()
# daily_buy_stat.columns=['均值']
# daily_buy_median = daily_buy.resample('1y').median()
# daily_buy_median.loc['全时段'] = daily_buy.median()
# daily_buy_median.columns=['中位数']
# daily_buy_percentile = []
# for pct in [0.2,0.4,0.6,0.8]:
#     temp = daily_buy.resample('1y').quantile(pct)
#     temp.loc['全时段'] = daily_buy.quantile(pct)
#     temp.columns=['%d分位数'%int(pct*100)]
#     daily_buy_percentile.append(temp)
#
# daily_buy_stat = pd.concat(daily_buy_percentile+[daily_buy_stat,daily_buy_median],axis=1)
# daily_buy_stat.index = daily_buy_stat.index.map(lambda x : str(x)[:4])
##########

net_compare = pd.concat(net_Value_list, axis=1).replace(0,np.nan).fillna(method='pad')
net_compare['year'] = [x // 10000 for x in net_compare.index]
yearly_drawdown_stat = {}
mdd_info = pd.DataFrame()
for year in list(set(net_compare['year'])) + [-1]:
    if year==-1:
        year = 'all'
        temp_prof_comp = net_compare.sort_index()
    else:
        temp_prof_comp = net_compare[net_compare['year'].eq(year)].sort_index()
    cummax = temp_prof_comp.cummax()
    cum_mdd = ( (cummax- temp_prof_comp)/temp_prof_comp).drop('year',axis=1)
    mdd_end = cum_mdd.idxmax()
    mdd_start = pd.Series()
    for model_name in mdd_end.index:
        try:
            top_val = cummax.loc[mdd_end[model_name],model_name]
        except:
            print(1)
        mdd_start[model_name] = cummax[model_name].eq(top_val).idxmax()
    mdd_period = pd.DataFrame({'start':mdd_start,'end':mdd_end}).T
    mdd_period['year'] = year
    mdd_period = mdd_period.reset_index().set_index(['year','index'])
    mdd_info = mdd_info.append(mdd_period)
    cum_mdd.index = pd.to_datetime(cum_mdd.index.astype(str))
    yearly_drawdown_stat[year] = cum_mdd

pre_date = get_pre_trade_date(net_compare.index[0])
net_compare = net_compare.reindex([pre_date]+net_compare.index.tolist())
net_compare.loc[pre_date,:] = 1
net_compare.index = pd.to_datetime(net_compare.index.astype(str))
net_compare = net_compare.drop('year', axis=1)

draw_down_info = pd.concat([yearly_drawdown_stat[x] for x in list(filter(lambda x : isinstance(x,int),list(yearly_drawdown_stat.keys())))])

wind_a = wind_a.loc[pre_date:]#s.get_factor_value('WIND_AIndexWindIndustriesEOD',S_INFO_WINDCODE=['881001.WI'])[['TRADE_DT','S_DQ_CLOSE']].set_index('TRADE_DT').loc['20160104':]
wind_a.index = wind_a.index.astype(str)
kcb_szzs = s.get_factor_value('Basic_factor',['000001.SH','399006.SZ','399001.SZ','000300.SH','000905.SH'],factor_names=['close'],mddate=wind_a.index.tolist())
kcb_szzs =kcb_szzs.reset_index().pivot_table(index='mddate',columns='stock',values='close').sort_index()

indexes = pd.concat([wind_a,kcb_szzs],axis=1).rename(columns=
                        {'S_DQ_CLOSE':'万德全A','000001.SH':'上证指数','399006.SZ':'创业板指',
                         '399001.SZ':'深证成指','000300.SH':'沪深300','000905.SH':'中证500'}).sort_index()
indexes.index = pd.to_datetime(indexes.index)

indexes = indexes.loc[net_compare.index]

index_daily_pct = indexes.pct_change()[1:]
index_daily_stat = {}
index_daily_stat['日胜率'] = pd.concat([(index_daily_pct>0).resample('1y').mean(),pd.DataFrame({'全时段':(index_daily_pct>0).mean()}).T])
index_daily_stat['收益率盈亏比'] = -1*pd.concat([index_daily_pct[index_daily_pct>0].resample('1y').mean()/index_daily_pct[index_daily_pct<0].resample('1y').mean(),
                                   pd.DataFrame({'全时段':index_daily_pct[index_daily_pct>0].mean()/index_daily_pct[index_daily_pct<0].mean()}).T])
index_daily_stat['收益率均值'] = pd.concat([index_daily_pct.resample('1y').mean(),pd.DataFrame({'全时段':index_daily_pct.mean()}).T])
index_daily_stat['收益率波动'] = pd.concat([index_daily_pct.resample('1y').std(),pd.DataFrame({'全时段':index_daily_pct.std()}).T])
index_daily_stat['年化夏普'] = (244**0.5)*index_daily_stat['收益率均值']/index_daily_stat['收益率波动']

index_daily_stat_df = []
for each in index_daily_stat:
    temp = index_daily_stat[each].T
    temp.columns = [int(x.strftime('%Y')) for x in temp.columns[:-1]] + [temp.columns[-1]]
    temp['indicator'] = each
    temp = temp.reset_index().set_index(['indicator','index'])
    index_daily_stat_df.append(temp)
index_daily_stat_df = pd.concat(index_daily_stat_df)
check = daily_stat.append(index_daily_stat_df).sort_index()
daily_stat = daily_stat.append(index_daily_stat_df).sort_index()

index_monthly_stat = indexes[1:].resample('1m').last() / indexes[1:].resample('1m').first() - 1
monthly_stat = {}
monthly_stat['月度收益率'] = pd.concat([net_compare[1:].resample('1m').last()/ net_compare[1:].resample('1m').first() - 1,
                                  index_monthly_stat], axis=1, join='inner')
monthly_stat['月度买入信号数'] = daily_buy.resample('1m').sum()
cum_profit = pd.concat(profit_list,axis=1)
cum_profit.index = pd.to_datetime(cum_profit.index.astype(str))
account_cap = pd.concat(account_cap,axis=1)
account_cap.index = pd.to_datetime(account_cap.index.astype(str))

net_compare = pd.concat([net_compare,indexes/indexes.loc[indexes.index[0]]],axis=1)
indexes = indexes.reindex(yearly_drawdown_stat['all'].index)


# pd.to_pickle([profit_list,daily_stat_list,signaly_stat_list],'/data/user/015664/AFuckingTrigger/XGB回归滚动阈值结果汇总.pkl')
# with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/剔除未来信息因子后-不同模型集成-全市场活跃股票池对比(含吴雨璘新添加的两个维度模型).xlsx') as writer:
all_file = f'{base_path}样本外策略参数寻优_不同股票池数量_threshold_0.04_per_ratio_0.02_.xlsx'
with pd.ExcelWriter(all_file) as writer:
    net_compare.to_excel(writer, sheet_name='账户净值对比')
    cum_profit.sort_index(axis=1).replace(0,np.nan).fillna(method='pad').to_excel(writer, sheet_name='账面累积收益')
    # daily_buy_stat.to_excel(writer, sheet_name='触发数量分布统计')
    holding_time_count.to_excel(writer,sheet_name='持仓时间统计')
    account_cap.sort_index(axis=1).to_excel(writer, sheet_name='持仓市值')
    daily_profit_rate_compare.to_excel(writer, sheet_name='单日收益率')
    ###############
    mdd_info.to_excel(writer, sheet_name='最大回撤区间')
    draw_down_info.to_excel(writer, sheet_name='累计最大回撤(逐年)')
    pd.concat([yearly_drawdown_stat['all'],indexes/indexes.loc[indexes.index[0]]],axis=1).to_excel(writer, sheet_name='累计最大回撤(全周期)')
    for each in monthly_stat:
        monthly_stat[each].to_excel(writer, sheet_name=each)
    monthly_stat['月度收益率'].corr().to_excel(writer, sheet_name='模型-指数间月度收益相关性')
    for each in monthly_pre_active.minor_axis:
        monthly_pre_active.loc[:,:,each].to_excel(writer, sheet_name=each)
    ###############
    cash_occupy_compare.to_excel(writer, sheet_name='占用资金')
    daily_holding.to_excel(writer, sheet_name='持仓股票数')
    daily_buy.to_excel(writer, sheet_name='每日触发数量')
    daily_stat.reset_index().set_index(['index', '模型']).sort_index().to_excel(writer, sheet_name='日收益综合统计')
    signaly_stat.reset_index().set_index(['index', '模型']).sort_index().to_excel(writer, sheet_name='按信号综合统计')

writer.close()
send_file(['015664'],all_file)
# (indexes.resample('1y').last()/indexes.resample('1y').first() - 1).to_excel('/data/user/015664/AFuckingTrigger/基于初始资金考虑成交_样本内指数_v3.xlsx')

from xquant.xqutils.helper import link
lm = link.LinkMessage()
lm.sendMessage("结果统计结束")


sensitive_compare = daily_stat.swaplevel(0,1).drop(['万德全A', '上证指数', '中证500', '创业板指', '沪深300', '深证成指']).swaplevel(0,1)#.reset_index()
sensitive_compare['per_ratio'] = sensitive_compare.index.map(lambda x : x[1].replace('per_ratio_','').replace('threshold_','').split('_'))
sensitive_compare['per_ratio'],sensitive_compare['threshold'] = sensitive_compare['per_ratio'].apply(lambda x : eval(x[0])),sensitive_compare['per_ratio'].apply(lambda x : eval(x[1]))


sensitivity_stat = {}
for items in ['净值最大回撤','年化夏普', '年化收益','收益率波动','收益率盈亏比', '日胜率']:
    sensitivity_stat[items] = sensitive_compare.loc[items].pivot_table(index='per_ratio',columns='threshold',values='全时段')

cash_occupy_stat = cash_occupy_compare.mean().to_frame()
cash_occupy_stat['per_ratio'] = cash_occupy_stat.index.map(lambda x : x.replace('per_ratio_','').replace('threshold_','').split('_'))
cash_occupy_stat['per_ratio'],cash_occupy_stat['threshold'] = cash_occupy_stat['per_ratio'].apply(lambda x : eval(x[0])),cash_occupy_stat['per_ratio'].apply(lambda x : eval(x[1]))
sensitivity_stat['平均占资'] = cash_occupy_stat.pivot_table(index='per_ratio',columns='threshold',values=0)

signal_profit = signaly_stat.loc['收益率']
signal_profit['per_ratio'] = signal_profit.index.map(lambda x : x.replace('per_ratio_','').replace('threshold_','').split('_'))
signal_profit['per_ratio'],signal_profit['threshold'] = signal_profit['per_ratio'].apply(lambda x : eval(x[0])),signal_profit['per_ratio'].apply(lambda x : eval(x[1]))

sensitivity_stat['单信号收益'] = signal_profit.pivot_table(index='per_ratio',columns='threshold',values='全时段')

with pd.ExcelWriter(f'{base_path}样本外策略参数寻优_敏感性分析.xlsx') as writer:
    for each in sensitivity_stat:
        sensitivity_stat[each].to_excel(writer,sheet_name=each)

writer.close()

from dataApi.sendInfo import send_file

send_file(['015664'],f'{base_path}样本外策略参数寻优_敏感性分析.xlsx')
send_file(['015664'],f'{base_path}样本外策略参数寻优.xlsx')