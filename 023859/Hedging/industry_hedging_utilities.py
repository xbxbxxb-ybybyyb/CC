import pandas as pd
import numpy as np
import os

assert os.system('pip install pulp') == 0
import pulp
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体，适用于 Windows
rcParams['axes.unicode_minus'] = False


def calc_profit(trading_days, strategy_list, root_dict, ZZ1000_buy_amt_daily, deviation, vote_num):
    start_date = int(trading_days[0])
    end_date = int(trading_days[-1])
    index_md = pd.read_pickle(root_dict['index_info'])
    index_md['931_941_twap'] = index_md[[931, 932, 933, 934, 935, 936, 937, 938, 939, 940]].mean(axis=1)
    index_md['twap'] = index_md.mean(axis=1)
    index_md['next_0931'] = index_md.groupby('Ticker')[931].shift(-1)
    index_md['next_twap'] = index_md.groupby('Ticker')['twap'].shift(-1)
    index_md['label_0931_next_0931'] = index_md['next_0931'] / index_md[931] - 1
    index_md['label_931_941_twap_next_twap'] = index_md['next_twap'] / index_md['931_941_twap'] - 1

    index_md_unstack = index_md.unstack()
    index_md_unstack = index_md_unstack.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

    # 读取指数成分股行业、权重、分钟价格数据
    ZZ1000_sw_weight_and_price = pd.read_pickle(root_dict['zz1000_info'])
    ZZ1000_sw_weight_and_price = ZZ1000_sw_weight_and_price[ZZ1000_sw_weight_and_price['STPT'] == False]
    ZZ1000_sw_weight_and_price['next_0931'] = ZZ1000_sw_weight_and_price.groupby('Ticker')['m931'].shift(-1)
    ZZ1000_sw_weight_and_price['label_0931_next_0931'] = ZZ1000_sw_weight_and_price['next_0931'] / ZZ1000_sw_weight_and_price['m931'] - 1
    ZZ1000_sw_weight_and_price = ZZ1000_sw_weight_and_price.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
    ZZ1000_sw_weight_and_price['label_931_941_twap_next_twap'] = ZZ1000_sw_weight_and_price['next_vwap_adj'] / ZZ1000_sw_weight_and_price['931_941_twap_adj'] - 1
    # ZZ1000_sw_weight_and_price['label_931_941_twap_next_twap'] = ZZ1000_sw_weight_and_price['next_twap'] / ZZ1000_sw_weight_and_price['931_941_twap'] - 1

    ZZ1000_sw_weight_and_price['industry_weight_sum'] = ZZ1000_sw_weight_and_price.groupby(['dt', 'sw_industry_code_1'])['weight'].transform('sum')
    ZZ1000_sw_weight_and_price['weight_in_industry'] = ZZ1000_sw_weight_and_price['weight'] / ZZ1000_sw_weight_and_price['industry_weight_sum']

    ZZ1000_groupby_industry = ZZ1000_sw_weight_and_price.reset_index().groupby(['dt', 'sw_industry_code_1'])[['weight']].sum()  # 按日期和行业统计zz1000成分股权重
    ZZ1000_groupby_industry['deviation_float'] = deviation[0]
    ZZ1000_groupby_industry['deviation_fix'] = deviation[1]
    ZZ1000_groupby_industry['weight_limit_float'] = ZZ1000_groupby_industry['weight'] * (1 + ZZ1000_groupby_industry['deviation_float'])  # 最大行业权重
    ZZ1000_groupby_industry['weight_limit_fix'] = ZZ1000_groupby_industry['weight'] + ZZ1000_groupby_industry['deviation_fix']# 固定权重
    ZZ1000_groupby_industry['weight_limit'] = ZZ1000_groupby_industry[['weight_limit_float','weight_limit_fix']].max(axis=1)
    ZZ1000_groupby_industry['buy_amt'] = ZZ1000_buy_amt_daily * ZZ1000_groupby_industry['weight']  # 行业在持有ZZ1000现货中的规模
    ZZ1000_groupby_industry['buy_amt_limit'] = ZZ1000_buy_amt_daily * ZZ1000_groupby_industry['weight_limit']  # 行业在投资组合中的规模上限

    ZZ1000_groupby_industry['total_sell'] = np.nan
    # 先设计买入端
    df_strategy_basic_sw1 = pd.read_pickle(root_dict['strategy_info'])
    df_strategy_basic_sw1 = df_strategy_basic_sw1[df_strategy_basic_sw1['strategy'].isin(strategy_list)]
    df_strategy_sign_sw1 = df_strategy_basic_sw1[df_strategy_basic_sw1['vote_sum_pred'] >= vote_num]
    df_strategy_sign_sw1['buy_amt'] = df_strategy_sign_sw1['label_buy_amt_200']
    df_strategy_sign_sw1['pct'] = df_strategy_sign_sw1['label_pct_200']
    '''
    if holding_day==1:
        mapping_buy_amt = {
            1: 'label_buy_amt_100',
            2: 'label_buy_amt_200',
            3: 'label_buy_amt_300',
            4: 'label_buy_amt_400',
            5: 'label_buy_amt_400',
            6: 'label_buy_amt_400',
        }
        mapping_pct = {
            1: 'label_pct_100',
            2: 'label_pct_200',
            3: 'label_pct_300',
            4: 'label_pct_400',
            5: 'label_pct_400',
            6: 'label_pct_400',
        }
        df_strategy_sign_sw1['buy_amt'] = df_strategy_sign_sw1.apply(lambda row: row[mapping_buy_amt[row['vote_sum_pred']]],axis=1)
        df_strategy_sign_sw1['pct'] = df_strategy_sign_sw1.apply(lambda row: row[mapping_pct[row['vote_sum_pred']]], axis=1)
    elif holding_day==2:
        mapping_buy_amt = {
            1: 'label_buy_amt_100_p2',
            2: 'label_buy_amt_200_p2',
            3: 'label_buy_amt_300_p2',
            4: 'label_buy_amt_400_p2',
            5: 'label_buy_amt_400_p2',
            6: 'label_buy_amt_400_p2',
        }
        mapping_pct = {
            1: 'label_pct_100_p2',
            2: 'label_pct_200_p2',
            3: 'label_pct_300_p2',
            4: 'label_pct_400_p2',
            5: 'label_pct_400_p2',
            6: 'label_pct_400_p2',
        }
        df_strategy_sign_sw1['buy_amt'] = df_strategy_sign_sw1.apply(lambda row: row[mapping_buy_amt[row['vote_sum_pred']]], axis=1)
        df_strategy_sign_sw1['pct'] = df_strategy_sign_sw1.apply(lambda row: row[mapping_pct[row['vote_sum_pred']]], axis=1)
    elif holding_day==3:
        mapping_buy_amt = {
            1: 'label_buy_amt_100_p3',
            2: 'label_buy_amt_200_p3',
            3: 'label_buy_amt_300_p3',
            4: 'label_buy_amt_400_p3',
            5: 'label_buy_amt_400_p3',
            6: 'label_buy_amt_400_p3',
        }
        mapping_pct = {
            1: 'label_pct_100_p3',
            2: 'label_pct_200_p3',
            3: 'label_pct_300_p3',
            4: 'label_pct_400_p3',
            5: 'label_pct_400_p3',
            6: 'label_pct_400_p3',
        }
        df_strategy_sign_sw1['buy_amt'] = df_strategy_sign_sw1.apply(lambda row: row[mapping_buy_amt[row['vote_sum_pred']]], axis=1)
        df_strategy_sign_sw1['pct'] = df_strategy_sign_sw1.apply(lambda row: row[mapping_pct[row['vote_sum_pred']]], axis=1)
    '''
    # df_strategy_sign_sw1['buy_amt'] = 1e6*df_strategy_sign_sw1['vote_sum_pred'] # 所有策略调整买入规模 TODO
    # df_strategy_sign_sw1['strategy_weight'] = df_strategy_sign_sw1['vote_sum_pred']**2 / 6
    # df_strategy_sign_sw1.loc[df_strategy_sign_sw1['strategy']=='saturn','strategy_weight'] *= 2
    # df_strategy_sign_sw1['strategy_weight'] = df_strategy_sign_sw1['strategy_weight'] / df_strategy_sign_sw1.groupby(['dt','sw_industry_code_1'])['strategy_weight'].transform('sum') # TODO
    df_strategy_sign_sw1 = df_strategy_sign_sw1.reset_index().set_index(['dt', 'Ticker', 'strategy']).sort_index()
    # 读取模拟收益文件
    # profit_ = []
    # for strategy in strategy_list:
    #     profit_strategy = pd.read_hdf(root_dict[f'{strategy}_profit_info'])
    #     profit_strategy['strategy'] = strategy
    #     profit_.append(profit_strategy)
    #
    # profit = pd.concat(profit_).reset_index().set_index(['dt', 'Ticker', 'strategy']).sort_index()
    # profit = profit.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
    df_strategy_sign_sw1['act_buy_amt'] = np.nan
    df_strategy_sign_sw1['buy_amt'] = df_strategy_sign_sw1['buy_amt'].replace(np.nan, 0)
    # df_strategy_sign_sw1['pct'] = profit['pct'] # 信号文件里面的label_pct不一定是原信号pct
    df_strategy_sign_sw1['pct'] = df_strategy_sign_sw1['pct'].replace(np.nan, 0)
    df_strategy_sign_sw1['profit'] = df_strategy_sign_sw1['buy_amt'] * (df_strategy_sign_sw1['pct'] - 0.004)  # europa、jupiter、metis、leda扣千2，saturn、ceres、mimas扣千4
    df_strategy_sign_sw1 = df_strategy_sign_sw1.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
    # 处理策略样本重合的情况
    # sum_by_ticker = df_strategy_sign_sw1.groupby(['dt','Ticker'])['buy_amt'].sum()
    # ratio = (df_strategy_sign_sw1['buy_amt']/sum_by_ticker).clip(upper=1)
    # df_strategy_sign_sw1['final_buy_amt'] = df_strategy_sign_sw1['buy_amt']*df_strategy_sign_sw1.index.map(ratio)

    start_date_ = trading_days[0]
    yesterday_buy_info = pd.DataFrame({
        'sw_industry_code_1': ZZ1000_groupby_industry.loc[pd.to_datetime(start_date_)].index,
        'total_buy': 0
    })
    yesterday_sell_info = pd.DataFrame({
        'sw_industry_code_1': ZZ1000_groupby_industry.loc[pd.to_datetime(start_date_)].index,
        'total_sell': 0
    }).set_index('sw_industry_code_1')

    day_df_industry_weight = []
    day_df_replace_weight = pd.DataFrame(index=trading_days, columns=['信号端权重','剩余现货替换比例'])
    for date in trading_days:
        date = pd.to_datetime(date)
        industry_name_dict = ZZ1000_sw_weight_and_price.loc[date].set_index('sw_industry_code_1')['sw_industry_name_1'].to_dict()
        if date not in df_strategy_sign_sw1.index.get_level_values(0).unique():
            day_df_replace_weight.loc[date, '剩余现货替换比例'] = 0
            yesterday_buy_info = yesterday_buy_info.rename(columns={'total_buy': 'yesterday_total_buy'})
            industry_weight_info = pd.merge(yesterday_buy_info,ZZ1000_groupby_industry.loc[date, 'weight'].reset_index(), on='sw_industry_code_1', how='right')
            industry_weight_info['yesterday_total_buy'] = industry_weight_info['yesterday_total_buy'].replace(np.nan, 0)

            industry_sell_capacity = pd.concat([ZZ1000_groupby_industry.loc[date]['buy_amt'], yesterday_sell_info['total_sell']], axis=1).fillna(0)
            industry_sell_capacity_dict = (industry_sell_capacity['buy_amt'] - industry_sell_capacity['total_sell']).clip_lower(0).to_dict()
            industry_weight_info['sell_capacity'] = industry_weight_info['sw_industry_code_1'].map(industry_sell_capacity_dict)
            industry_weight_info['strategy_allocation'] = industry_weight_info['sell_capacity'] + industry_weight_info['yesterday_total_buy']
            industry_weight_info['strategy_weight'] = industry_weight_info['strategy_allocation'] / industry_weight_info['strategy_allocation'].sum()
            industry_weight_info['t-1_buy_weight'] = industry_weight_info['yesterday_total_buy'] / industry_weight_info['strategy_allocation'].sum()
            industry_weight_info['t_buy_weight'] = 0
            industry_weight_info['t_zz1000_weight'] = industry_weight_info['sell_capacity'] / industry_weight_info['strategy_allocation'].sum()
            industry_weight_info['dt'] = date
            industry_weight_info['sw_industry_name_1'] = industry_weight_info['sw_industry_code_1'].map(industry_name_dict)

            day_df_replace_weight.loc[date, '信号端权重'] = industry_weight_info['yesterday_total_buy'].sum() / (industry_weight_info['sell_capacity'].sum() + industry_weight_info['yesterday_total_buy'].sum())
            day_df_industry_weight.append(industry_weight_info[['dt', 'sw_industry_code_1', 'sw_industry_name_1', 'weight','strategy_weight', 't-1_buy_weight', 't_buy_weight', 't_zz1000_weight']])

            yesterday_buy_info = pd.DataFrame({
                'sw_industry_code_1': ZZ1000_groupby_industry.loc[date].index,
                'total_buy': 0
            })
            yesterday_sell_info = pd.DataFrame({
                'sw_industry_code_1': ZZ1000_groupby_industry.loc[date].index,
                'total_sell': 0
            }).set_index('sw_industry_code_1')
            continue

        industry_deviation_up_dict = ZZ1000_groupby_industry.loc[date]['buy_amt_limit'].to_dict()
        industry_sell_capacity = pd.concat([ZZ1000_groupby_industry.loc[date]['buy_amt'], yesterday_sell_info['total_sell']], axis=1).fillna(0)
        industry_sell_capacity_dict = (industry_sell_capacity['buy_amt'] - industry_sell_capacity['total_sell']).clip_lower(0).to_dict()
        df_strategy_sign_sw1_date = df_strategy_sign_sw1.loc[date]

        industries = df_strategy_sign_sw1_date['sw_industry_code_1'].unique()
        for j in industries:
            mask = (df_strategy_sign_sw1_date['sw_industry_code_1'] == j)
            yesterday_buy = yesterday_buy_info[yesterday_buy_info['sw_industry_code_1'] == j]['total_buy']
            yesterday_buy = yesterday_buy.iloc[0] if not yesterday_buy.empty else 0
            df_strategy_sign_sw1_date.loc[mask, 'act_buy_amt'] = min(2e6, max(0, industry_deviation_up_dict[j] - yesterday_buy)/len(df_strategy_sign_sw1_date.loc[mask]))

        adjusted_ratio = min(1, (ZZ1000_buy_amt_daily - yesterday_buy_info['total_buy'].sum()) / df_strategy_sign_sw1_date['act_buy_amt'].sum())
        df_strategy_sign_sw1_date['act_buy_amt'] *= adjusted_ratio
        '''
        prob = pulp.LpProblem('Determine_Act_Buy_Amt', pulp.LpMaximize)
        df_strategy_sign_sw1_date['var'] = df_strategy_sign_sw1_date.index
        buy_vars = pulp.LpVariable.dicts('Buy', df_strategy_sign_sw1_date['var'], lowBound=0, cat='Continuous')
        prob += pulp.lpSum([df_strategy_sign_sw1_date.loc[i, 'vote_sum_pred'] * buy_vars[i] for i in df_strategy_sign_sw1_date['var']]), 'Total_Signal_Weighted_Buy'
        # 添加约束条件
        for i in df_strategy_sign_sw1_date['var']:
            # vote_num_ratio = min(df_strategy_sign_sw1_date.loc[i,'vote_sum_pred'] / 4, 1)
            # prob += buy_vars[i] <= vote_num_ratio * 4e6, f'Max_Buy_Sample_{i}'
            prob += buy_vars[i] <=  2e6, f'Max_Buy_Sample_{i}'
            # if i[1] in ['ceres', 'mimas', 'p4']:
            #     prob += buy_vars[i] <= vote_num_ratio*5e6, f'Max_Buy_Sample_{i}'
            # elif i[1] == 'saturn':
            #     prob += buy_vars[i] <= vote_num_ratio*1e7, f'Max_Buy_Sample_{i}'
        # 行业偏离度限制
        industries = df_strategy_sign_sw1_date['sw_industry_code_1'].unique()
        for j in industries:
            yesterday_buy = yesterday_buy_info[yesterday_buy_info['sw_industry_code_1'] == j]['total_buy']
            yesterday_buy = yesterday_buy.iloc[0] if not yesterday_buy.empty else 0
            indices = df_strategy_sign_sw1_date[df_strategy_sign_sw1_date['sw_industry_code_1'] == j].index
            prob += pulp.lpSum([buy_vars[i] for i in indices]) <= max(0, industry_deviation_up_dict[j] - yesterday_buy), f'Max_Buy_Industry_{j}'
        # 每日总买入额度限制
        prob += pulp.lpSum([buy_vars[i] for i in df_strategy_sign_sw1_date['var']]) <= ZZ1000_buy_amt_daily - yesterday_buy_info['total_buy'].sum(), 'Max_Daily_Buy'
        prob.solve()
        if pulp.LpStatus[prob.status] != 'Optimal':
            print(f'求解状态：{pulp.LpStatus[prob.status]}')
            raise Exception('线性规划问题未能找到最优解')
    
        df_strategy_sign_sw1_date['act_buy_amt'] = [pulp.value(buy_vars[i]) for i in df_strategy_sign_sw1_date['var']]
        '''
        # df_strategy_sign_sw1_date['act_buy_amt'] = df_strategy_sign_sw1_date.groupby(['vote_sum_pred','sw_industry_code_1'])['act_buy_amt'].transform('sum')*df_strategy_sign_sw1_date['strategy_weight'] # TODO
        # df_strategy_sign_sw1_date = pd.merge(df_strategy_sign_sw1_date.reset_index().drop('act_buy_amt', axis=1),df_strategy_sign_sw1_date.groupby(['sw_industry_code_1','strategy_weight'])['act_buy_amt'].mean().reset_index(),on=['sw_industry_code_1','strategy_weight'])
        # df_strategy_sign_sw1_date = pd.merge(df_strategy_sign_sw1_date.reset_index().drop('act_buy_amt', axis=1),df_strategy_sign_sw1_date.groupby(['sw_industry_code_1','vote_sum_pred'])['act_buy_amt'].mean().reset_index(),on=['sw_industry_code_1','vote_sum_pred'])
        # df_strategy_sign_sw1_date = df_strategy_sign_sw1_date.set_index(['Ticker', 'strategy'])

        df_strategy_sign_sw1_date['act_buy_amt'] = df_strategy_sign_sw1_date[['act_buy_amt', 'buy_amt']].min(axis=1)
        df_strategy_sign_sw1.loc[date]['act_buy_amt'] = df_strategy_sign_sw1_date['act_buy_amt']
        total_buy = df_strategy_sign_sw1_date['act_buy_amt'].sum()

        buy_per_industry = df_strategy_sign_sw1_date.groupby('sw_industry_code_1')['act_buy_amt'].sum().reset_index()
        buy_per_industry.rename(columns={'act_buy_amt': 'total_buy'}, inplace=True)

        # 确定卖出端
        signal_strength_per_industry = df_strategy_sign_sw1_date.groupby('sw_industry_code_1')['vote_sum_pred'].sum().reset_index()
        signal_strength_per_industry.rename(columns={'vote_sum_pred': 'total_signal_strength'}, inplace=True)

        buy_info = pd.merge(buy_per_industry, signal_strength_per_industry, on='sw_industry_code_1')

        buy_info['sell_capacity'] = buy_info['sw_industry_code_1'].map(industry_sell_capacity_dict)
        buy_info['sell_same'] = buy_info[['total_buy', 'sell_capacity']].min(axis=1)

        buy_info['excess_buy'] = buy_info['total_buy'] - buy_info['sell_same']
        total_excess = buy_info['excess_buy'].sum()
        buy_info['sell_other'] = 0

        signal_industries = buy_info['sw_industry_code_1'].tolist()
        non_signal_industries = [j for j in industry_sell_capacity_dict.keys() if j not in signal_industries]

        buy_info['available_sell'] = buy_info['sell_capacity'] - buy_info['sell_same']
        available_sell_signal = buy_info[buy_info['available_sell'] > 0].copy()
        total_available_sell_signal = available_sell_signal['available_sell'].sum()

        non_signal_sell_capacity = {j: industry_sell_capacity_dict[j] for j in non_signal_industries}
        available_sell_non_signal = {j: cap for j, cap in non_signal_sell_capacity.items()}
        total_available_sell_non_signal = sum(available_sell_non_signal.values())

        total_available_sell = total_available_sell_signal + total_available_sell_non_signal

        if total_available_sell > 0:
            available_sell_signal['sell_other'] = (available_sell_signal['available_sell'] / total_available_sell) * total_excess
            buy_info.loc[buy_info['sw_industry_code_1'].isin(available_sell_signal['sw_industry_code_1']), 'sell_other'] = available_sell_signal['sell_other']

            for j, cap in available_sell_non_signal.items():
                sell_amount = (cap / total_available_sell) * total_excess
                buy_info = buy_info.append({
                    'sw_industry_code_1': j,
                    'total_buy': 0.0,
                    'total_signal_strength': 0.0,
                    'sell_capacity': cap,
                    'sell_same': 0.0,
                    'excess_buy': 0.0,
                    'sell_other': sell_amount
                }, ignore_index=True)

        buy_info['total_sell'] = buy_info['sell_same'] + buy_info['sell_other']

        day_df_replace_weight.loc[date, '剩余现货替换比例'] = total_buy / buy_info['sell_capacity'].sum()
        day_df_replace_weight.loc[date, '信号端权重'] = (total_buy + yesterday_buy_info['total_buy'].sum()) / (buy_info['sell_capacity'].sum() + yesterday_buy_info['total_buy'].sum())

        yesterday_sell_info = buy_info[['sw_industry_code_1', 'total_sell']].set_index('sw_industry_code_1')
        ZZ1000_groupby_industry.loc[date]['total_sell'] = buy_info.set_index('sw_industry_code_1')['total_sell']

        industry_weight_info = buy_info.copy()
        industry_weight_info = industry_weight_info[industry_weight_info['sw_industry_code_1'].isin(ZZ1000_groupby_industry.loc[date].index)]
        yesterday_buy_info = yesterday_buy_info.rename(columns={'total_buy': 'yesterday_total_buy'})
        industry_weight_info = pd.merge(industry_weight_info, yesterday_buy_info, on='sw_industry_code_1', how='left')
        industry_weight_info['yesterday_total_buy'] = industry_weight_info['yesterday_total_buy'].replace(np.nan, 0)

        industry_weight_info = pd.merge(industry_weight_info, ZZ1000_groupby_industry.loc[date, 'weight'].reset_index(), on='sw_industry_code_1', how='left')

        industry_weight_info['strategy_allocation'] = industry_weight_info['sell_capacity'] + industry_weight_info['yesterday_total_buy'] + industry_weight_info['total_buy'] - industry_weight_info['total_sell']
        industry_weight_info['strategy_weight'] = industry_weight_info['strategy_allocation'] / industry_weight_info['strategy_allocation'].sum()
        industry_weight_info['t-1_buy_weight'] = industry_weight_info['yesterday_total_buy'] / industry_weight_info['strategy_allocation'].sum()
        industry_weight_info['t_buy_weight'] = industry_weight_info['total_buy'] / industry_weight_info['strategy_allocation'].sum()
        industry_weight_info['t_zz1000_weight'] = (industry_weight_info['sell_capacity'] - industry_weight_info['total_sell']) / industry_weight_info['strategy_allocation'].sum()

        industry_weight_info['dt'] = date
        industry_weight_info['sw_industry_name_1'] = industry_weight_info['sw_industry_code_1'].map(industry_name_dict)
        day_df_industry_weight.append(industry_weight_info[['dt', 'sw_industry_code_1', 'sw_industry_name_1', 'weight', 'strategy_weight', 't-1_buy_weight','t_buy_weight', 't_zz1000_weight']])
        yesterday_buy_info = buy_per_industry.copy()

    day_df_industry_weight = pd.concat(day_df_industry_weight)
    df_strategy_sign_sw1['act_profit'] = df_strategy_sign_sw1['act_buy_amt'] * (df_strategy_sign_sw1['pct'] - 0.004)  # 策略端实际扣费收益

    ZZ1000_sw_weight_and_price = ZZ1000_sw_weight_and_price.reset_index().merge(ZZ1000_groupby_industry[['total_sell']].reset_index(), on=['dt', 'sw_industry_code_1'], how='left').set_index(['dt', 'Ticker'])
    ZZ1000_sw_weight_and_price['act_sell_amt'] = ZZ1000_sw_weight_and_price['total_sell'] * ZZ1000_sw_weight_and_price['weight_in_industry']
    ZZ1000_sw_weight_and_price['act_profit_0931_next_0931'] = -ZZ1000_sw_weight_and_price['act_sell_amt'] * (ZZ1000_sw_weight_and_price['label_0931_next_0931'] + 0.001)
    ZZ1000_sw_weight_and_price['act_profit_931_941_twap_next_twap'] = -ZZ1000_sw_weight_and_price['act_sell_amt'] * (ZZ1000_sw_weight_and_price['label_931_941_twap_next_twap'] + 0.001)

    # 按日生成回测结果
    day_df_strategy = pd.DataFrame()

    day_df_strategy['000852.SH_label_0931_next_0931'] = index_md_unstack[('label_0931_next_0931', '000852.SH')]
    day_df_strategy['000852.SH_label_931_941_twap_next_twap'] = index_md_unstack[('label_931_941_twap_next_twap', '000852.SH')]  # profit.groupby('dt')['index_pct'].mean() #模拟收益文件中若有指数收益率，以模拟收益文件为主

    day_df_strategy['剩余现货替换比例'] = day_df_replace_weight['剩余现货替换比例']
    day_df_strategy['信号端权重'] = day_df_replace_weight['信号端权重']

    merged_df = ZZ1000_sw_weight_and_price[['act_sell_amt']].merge(df_strategy_sign_sw1[['act_buy_amt']], left_index=True, right_index=True, how='inner')
    merged_df['min_amt'] = merged_df[['act_sell_amt', 'act_buy_amt']].min(axis=1)
    daily_min_sum = merged_df.groupby('dt')['min_amt'].sum()
    daily_sell_sum = ZZ1000_sw_weight_and_price.groupby('dt')['act_sell_amt'].sum()
    day_df_strategy['zz1000成分股权重'] = (daily_min_sum / daily_sell_sum).fillna(0)

    strategy_join = '+'.join(strategy_list)
    day_df_strategy[f'{strategy_join}信号样本买入规模'] = df_strategy_sign_sw1.groupby('dt')['buy_amt'].sum()
    day_df_strategy[f'{strategy_join}信号样本买入规模'] = day_df_strategy[f'{strategy_join}信号样本买入规模'].fillna(0)
    day_df_strategy[f'{strategy_join}指数完全对冲多头暴露'] = 0
    day_df_strategy[f'{strategy_join}行业完全对冲信号实际买入规模'] = df_strategy_sign_sw1.groupby('dt')['act_buy_amt'].sum()
    day_df_strategy[f'{strategy_join}行业完全对冲信号实际买入规模'] = day_df_strategy[f'{strategy_join}行业完全对冲信号实际买入规模'].fillna(0)

    day_df_strategy[f'{strategy_join}行业完全对冲信号多头暴露'] = day_df_strategy[f'{strategy_join}行业完全对冲信号实际买入规模'] - ZZ1000_groupby_industry['total_sell'].groupby('dt').sum()

    day_df_strategy[f'{strategy_join}指数收益'] = -day_df_strategy[f'{strategy_join}信号样本买入规模'] * day_df_strategy['000852.SH_label_931_941_twap_next_twap']
    day_df_strategy[f'{strategy_join}行业收益'] = ZZ1000_sw_weight_and_price.groupby('dt')['act_profit_931_941_twap_next_twap'].sum()
    day_df_strategy[f'{strategy_join}_act_profit'] = df_strategy_sign_sw1.groupby('dt')['act_profit'].sum()
    day_df_strategy[f'{strategy_join}_act_profit'] = day_df_strategy[f'{strategy_join}_act_profit'].fillna(0)

    # 行业对冲收益
    day_df_strategy[f'{strategy_join}行业完全对冲'] = day_df_strategy[f'{strategy_join}_act_profit'] + day_df_strategy[f'{strategy_join}行业收益']
    day_df_strategy[f'{strategy_join}原信号'] = df_strategy_sign_sw1.groupby('dt')['profit'].sum()
    day_df_strategy[f'{strategy_join}原信号'] = day_df_strategy[f'{strategy_join}原信号'].fillna(0)
    day_df_strategy[f'{strategy_join}指数完全对冲'] = day_df_strategy[f'{strategy_join}原信号'] + day_df_strategy[f'{strategy_join}指数收益']
    day_df_strategy[f'{strategy_join}行业完全对冲信号端'] = day_df_strategy[f'{strategy_join}_act_profit']

    if len(strategy_list)>=1:
        for strategy in strategy_list:
            day_df_strategy[f'{strategy}信号样本买入规模'] = df_strategy_sign_sw1[df_strategy_sign_sw1.index.get_level_values(2) == strategy].groupby('dt')['buy_amt'].sum()
            day_df_strategy[f'{strategy}信号样本买入规模'] = day_df_strategy[f'{strategy}信号样本买入规模'].fillna(0)
            # 分策略统计
            day_df_strategy[f'{strategy}行业完全对冲信号样本买入规模'] = df_strategy_sign_sw1[df_strategy_sign_sw1.index.get_level_values(2) == strategy].groupby('dt')['act_buy_amt'].sum()
            day_df_strategy[f'{strategy}行业完全对冲信号样本买入规模'] = day_df_strategy[f'{strategy}行业完全对冲信号样本买入规模'].fillna(0)

            day_df_strategy[f'{strategy}指数完全对冲多头暴露'] = 0
            day_df_strategy[f'{strategy}指数收益'] = -day_df_strategy[f'{strategy}信号样本买入规模'] * day_df_strategy['000852.SH_label_931_941_twap_next_twap']
            day_df_strategy[f'{strategy}原信号'] = df_strategy_sign_sw1[df_strategy_sign_sw1.index.get_level_values(2) == strategy].groupby('dt')['profit'].sum()
            day_df_strategy[f'{strategy}原信号'] = day_df_strategy[f'{strategy}原信号'].fillna(0)
            day_df_strategy[f'{strategy}指数完全对冲'] = day_df_strategy[f'{strategy}原信号'] + day_df_strategy[f'{strategy}指数收益']
            # 分策略统计
            day_df_strategy[f'{strategy}行业完全对冲信号样本收益'] = df_strategy_sign_sw1[df_strategy_sign_sw1.index.get_level_values(2) == strategy].groupby('dt')['act_profit'].sum()
            day_df_strategy[f'{strategy}行业完全对冲信号样本收益'] = day_df_strategy[f'{strategy}行业完全对冲信号样本收益'].fillna(0)

    day_df_strategy.index = pd.to_datetime(day_df_strategy.index)

    return day_df_strategy, day_df_industry_weight, df_strategy_sign_sw1, ZZ1000_sw_weight_and_price


def sta_profit(profit, sign_buy_amt, long_exposure):
    res = {}
    res['信号日均规模（万元）'] = sign_buy_amt.mean() / 10000
    res['日均多头暴露（万元）'] = long_exposure.mean() / 10000
    res['收益（万元）'] = profit.sum() / 10000
    res['最大回撤（万元）'] = (profit.cumsum().cummax() - profit.cumsum()).max() / 10000
    res['收益风险比'] = res['收益（万元）'] / res['最大回撤（万元）']
    res['日扣费胜率'] = len(profit[profit > 0]) / len(profit[profit != 0])
    roll_profit = profit.rolling(3, min_periods=1).sum()
    res['收益夏普比'] = roll_profit.mean() / roll_profit.std() * 250 ** 0.5
    return pd.Series(res)