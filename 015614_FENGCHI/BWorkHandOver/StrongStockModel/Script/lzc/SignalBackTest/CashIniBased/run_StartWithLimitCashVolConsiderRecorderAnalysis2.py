# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py

import pandas as pd
import numpy as np
from dataApi.getData import get_daily_1stock
# out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/NoFutureInfoRes/XGB_HX_WYL_OnlineTestRevTriggerFilterHolding_Concept_deal_ratio_0.1_per_ratio_0.0050_threshold_0.050000.2VolConsider_UpBuy100_10bp_cost.xlsx'
out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/NoFutureInfoRes/XGB_HX_WYL_OnlineTestRevTriggerFilterHolding_deal_ratio_0.1_per_ratio_0.0050_threshold_0.050000.2VolConsider_UpBuy100_10bp_cost.xlsx'

res = pd.read_excel(out_file,sheet_name=None)
trading_record = res['逐笔持仓统计']
trading_record['start_date'],trading_record['end_date'] = trading_record['start']//10000,trading_record['end']//10000

res_pn,_ = pd.read_pickle(  '/data/user/015664/AFuckingTrigger/限制买入和持仓/NoFutureInfoRes/record/XGB_HX_WYL_daily_res_pn.pkl')

target_date = [20170726,20170804,20180309,20180319]
pre_date = [res_pn.major_axis[res_pn.major_axis.tolist().index(x)-1 ]for x in target_date]
stat = {}
for date,pre in zip(target_date,pre_date):
    if date==20180319:
        print(1)
    T_day_info = res_pn.loc[:, date, :]
    T_day_info = T_day_info.T[T_day_info.count() > 0]
    pre_date_info  = res_pn.loc[T_day_info.index, pre, :].T
    day_stat = pd.DataFrame(columns=['昨日收盘持仓市值','今日买入时点','今日买入成本','今日卖出时点','今日卖出市值','今日收盘持仓市值',
                                     '买入至收盘贡献收益','昨日收盘至今日卖出贡献收益','昨日持仓至今日贡献收益','今日该股票贡献收益'], index=T_day_info.index)
    day_stat['昨日收盘持仓市值'] = pre_date_info.loc[T_day_info.index,'收盘持仓市值']
    day_stat['今日收盘持仓市值'] = T_day_info.loc[T_day_info.index,'收盘持仓市值']
    start_record = trading_record[trading_record['start_date'].eq(date)].set_index('stk_id')
    end_record = trading_record[trading_record['end_date'].eq(date)].set_index('stk_id')
    day_stat['今日该股票贡献收益'] = 0
    for stk in T_day_info.index:
        if stk == 2008:
            print(1)
        if stk in start_record.index:
            day_stat.loc[stk,'今日买入成本'] = start_record.loc[stk,'cash_occupy']*1.001
            day_stat.loc[stk,'今日买入时点'] =  start_record.loc[stk,'start']%10000
            day_stat.loc[stk,'买入至收盘贡献收益'] = day_stat.loc[stk,'今日收盘持仓市值'] - day_stat.loc[stk,'今日买入成本']
        if stk in end_record.index:
            day_stat.loc[stk, '今日卖出市值'] = day_stat.loc[stk].fillna(0).loc['今日买入成本']-T_day_info.loc[stk].fillna(0).loc['扣费后净买入']
            day_stat.loc[stk, '今日卖出时点'] = end_record.loc[stk, 'end'] % 10000
            day_stat.loc[stk,'昨日收盘至今日卖出贡献收益'] = day_stat.loc[stk,'今日卖出市值'] - day_stat.loc[stk,'昨日收盘持仓市值']
        if not stk in end_record.index and not stk in start_record.index:
            if not np.isnan(T_day_info.loc[stk,'扣费后净买入']):
                day_stat.loc[stk, '今日卖出市值'] = day_stat.loc[stk].fillna(0).loc['今日买入成本'] - T_day_info.loc[stk].fillna(0).loc['扣费后净买入']
                close_adj = get_daily_1stock(stk,['close_badj'])
                pct_change = close_adj.loc[[pre,date],'close_badj'].pct_change().loc[date]
                day_stat.loc[stk, '昨日持仓至今日贡献收益'] = day_stat.loc[stk, '今日收盘持仓市值'] - day_stat.loc[stk, '今日收盘持仓市值']/(1+pct_change)
                #今日卖出部分昨日持仓市值
                sold_preday_cap = day_stat.loc[stk,'昨日收盘持仓市值'] - day_stat.loc[stk, '今日收盘持仓市值']/(1+pct_change)
                day_stat.loc[stk, '昨日收盘至今日卖出贡献收益'] = day_stat.loc[stk,'今日卖出市值'] - sold_preday_cap
            else:
                day_stat.loc[stk,'昨日持仓至今日贡献收益'] = day_stat.loc[stk,'今日收盘持仓市值'] - day_stat.loc[stk,'昨日收盘持仓市值']
        day_stat['今日该股票贡献收益'] = day_stat[[ '买入至收盘贡献收益','昨日收盘至今日卖出贡献收益','昨日持仓至今日贡献收益']].sum(axis=1)
    stat[date] = day_stat

    # (day_stat['今日收盘持仓市值'].fillna(0) - day_stat['昨日收盘持仓市值'].fillna(0) - (day_stat['今日买入成本'].fillna(0) - day_stat['今日卖出市值'].fillna(0))).sum()
    # (day_stat['今日收盘持仓市值'].fillna(0) - day_stat['昨日收盘持仓市值'].fillna(0) - T_day_info['扣费后净买入'].fillna(0)).sum()
    check_difference = (day_stat['今日买入成本'].fillna(0) - day_stat['今日卖出市值'].fillna(0))-T_day_info['扣费后净买入'].fillna(0)
    check_difference = check_difference[~np.isclose(check_difference,0)]
    # day_stat['今日该股票贡献收益'].sum()
for date in stat:
    print(date,stat[date]['今日该股票贡献收益'].sum())

with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号查验/三模型-全市场-个股票收益明细统计.xlsx') as writer:
    for date in stat:
        stat[date].to_excel(writer,sheet_name=str(date))

writer.close()

    # (day_stat['今日收盘持仓市值'].fillna(0) - day_stat['今日买入成本'].fillna(0) + day_stat['今日卖出市值'].fillna(0) - day_stat['昨日收盘持仓市值'].fillna(0)).sum()

    # day_stat['今日买入成本'].fillna(0) - day_stat['今日卖出市值'].fillna(0) - T_day_info['扣费后净买入']

    # day_stat['真实贡献'] = (day_stat['今日收盘持仓市值'].fillna(0) - day_stat['昨日收盘持仓市值'].fillna(0) - (day_stat['今日买入成本'].fillna(0) - day_stat['今日卖出市值'].fillna(0)))
    # day_stat['扣费后净买入']
# res = pd.read_excel('/data/user/015664/AFuckingTrigger/限制买入和持仓/NoFutureInfoRes/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost)),sheet_name=None)
#
# trade_record = res['逐笔持仓统计']
# trade_record
