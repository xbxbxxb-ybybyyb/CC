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
    ZZ1000_sw_weight_and_price['strategy'] = 'zz1000'
    ZZ1000_sw_weight_and_price['vote_sum_pred'] = 0
    ZZ1000_sw_weight_and_price['buy_amt'] = ZZ1000_buy_amt_daily*ZZ1000_sw_weight_and_price['weight']
    ZZ1000_sw_weight_and_price = ZZ1000_sw_weight_and_price.reset_index().set_index(['dt', 'Ticker', 'strategy']).sort_index()

    ZZ1000_sw_weight_and_price['next_0931'] = ZZ1000_sw_weight_and_price.groupby('Ticker')['m931'].shift(-1)
    ZZ1000_sw_weight_and_price['label_0931_next_0931'] = ZZ1000_sw_weight_and_price['next_0931'] / ZZ1000_sw_weight_and_price['m931'] - 1
    ZZ1000_sw_weight_and_price = ZZ1000_sw_weight_and_price.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
    ZZ1000_sw_weight_and_price['label_931_941_twap_next_twap'] = ZZ1000_sw_weight_and_price['next_twap'] / ZZ1000_sw_weight_and_price['931_941_twap'] - 1

    ZZ1000_sw_weight_and_price['industry_weight_sum'] = ZZ1000_sw_weight_and_price.groupby(['dt', 'sw_industry_code_1'])['weight'].transform('sum')
    ZZ1000_sw_weight_and_price['weight_in_industry'] = ZZ1000_sw_weight_and_price['weight'] / ZZ1000_sw_weight_and_price['industry_weight_sum']
    ZZ1000_sw_weight_and_price['act_sell_amt'] = np.nan


    ZZ1000_groupby_industry = ZZ1000_sw_weight_and_price.reset_index().groupby(['dt', 'sw_industry_code_1'])[['weight']].sum()  # 按日期和行业统计zz1000成分股权重
    ZZ1000_groupby_industry['deviation'] = deviation
    ZZ1000_groupby_industry['weight_limit'] = ZZ1000_groupby_industry['weight'] * (1 + ZZ1000_groupby_industry['deviation'])  # 最大行业权重
    ZZ1000_groupby_industry['buy_amt'] = ZZ1000_buy_amt_daily * ZZ1000_groupby_industry['weight']  # 行业在持有ZZ1000现货中的规模
    ZZ1000_groupby_industry['buy_amt_limit'] = ZZ1000_buy_amt_daily * ZZ1000_groupby_industry['weight_limit']  # 行业在投资组合中的规模上限

    # 先设计买入端
    df_strategy_basic_sw1 = pd.read_pickle(root_dict['strategy_info'])
    df_strategy_basic_sw1 = df_strategy_basic_sw1.drop_duplicates()
    df_strategy_basic_sw1 = df_strategy_basic_sw1[df_strategy_basic_sw1['strategy'].isin(strategy_list)]

    df_strategy_sign_sw1 = df_strategy_basic_sw1[df_strategy_basic_sw1['vote_sum_pred'] >= vote_num]
    df_strategy_sign_sw1 = df_strategy_sign_sw1.reset_index().set_index(['dt', 'Ticker', 'strategy']).sort_index()
    # 读取模拟收益文件
    profit_ = []
    for strategy in strategy_list:
        profit_strategy = pd.read_hdf(root_dict[f'{strategy}_profit_info'])
        profit_strategy['strategy'] = strategy
        profit_.append(profit_strategy)

    profit = pd.concat(profit_).reset_index().set_index(['dt', 'Ticker', 'strategy']).sort_index()
    profit = profit.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
    df_strategy_sign_sw1['act_buy_amt'] = np.nan
    df_strategy_sign_sw1['buy_amt'] = df_strategy_sign_sw1['buy_amt'].replace(np.nan, 0)
    df_strategy_sign_sw1['pct'] = profit['pct'] # 信号文件里面的label_pct不一定是原信号pct
    df_strategy_sign_sw1['pct'] = df_strategy_sign_sw1['pct'].replace(np.nan, 0)
    df_strategy_sign_sw1['profit'] = df_strategy_sign_sw1['buy_amt'] * (df_strategy_sign_sw1['pct'] - 0.004)  # europa、jupiter、metis、leda扣千2，saturn、ceres、mimas扣千4
    df_strategy_sign_sw1 = df_strategy_sign_sw1.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

    start_date_ = trading_days[0]

    yesterday_buy_info_by_ticker = pd.DataFrame({
        'act_buy_amt_t-1': 0,
        'CNLTS_BETA': df_strategy_sign_sw1.loc[pd.to_datetime(start_date_),'CNLTS_BETA'],
        'CNLTS_LIQUIDTY': df_strategy_sign_sw1.loc[pd.to_datetime(start_date_),'CNLTS_LIQUIDTY'],
        'CNLTS_MOMENTUM': df_strategy_sign_sw1.loc[pd.to_datetime(start_date_),'CNLTS_MOMENTUM'],
        'CNLTS_RESVOL': df_strategy_sign_sw1.loc[pd.to_datetime(start_date_),'CNLTS_RESVOL'],
        'CNLTS_SIZE': df_strategy_sign_sw1.loc[pd.to_datetime(start_date_),'CNLTS_SIZE'],
        'sw_industry_code_1': df_strategy_sign_sw1.loc[pd.to_datetime(start_date_),'sw_industry_code_1']
    })
    yesterday_sell_info_by_ticker = pd.DataFrame({
        'act_sell_amt_t-1': 0,
        'CNLTS_BETA': ZZ1000_sw_weight_and_price.loc[pd.to_datetime(start_date_),'CNLTS_BETA'],
        'CNLTS_LIQUIDTY': ZZ1000_sw_weight_and_price.loc[pd.to_datetime(start_date_), 'CNLTS_LIQUIDTY'],
        'CNLTS_MOMENTUM': ZZ1000_sw_weight_and_price.loc[pd.to_datetime(start_date_), 'CNLTS_MOMENTUM'],
        'CNLTS_RESVOL': ZZ1000_sw_weight_and_price.loc[pd.to_datetime(start_date_), 'CNLTS_RESVOL'],
        'CNLTS_SIZE': ZZ1000_sw_weight_and_price.loc[pd.to_datetime(start_date_), 'CNLTS_SIZE'],
        'sw_industry_code_1': ZZ1000_sw_weight_and_price.loc[pd.to_datetime(start_date_),'sw_industry_code_1']
    })

    day_df_industry_weight = []
    day_df_replace_weight = pd.DataFrame(index=trading_days, columns=['信号端权重','剩余现货替换比例'])
    for date in trading_days:
        date = pd.to_datetime(date)
        industry_name_dict = ZZ1000_sw_weight_and_price.loc[date].set_index('sw_industry_code_1')['sw_industry_name_1'].to_dict()
        if date not in df_strategy_sign_sw1.index.get_level_values(0).unique():
            zz1000_sw_weight_and_price_date = ZZ1000_sw_weight_and_price.loc[date]
            # t日无信号买入，无替换
            day_df_replace_weight.loc[date, '剩余现货替换比例'] = 0
            # 统计昨日买入情况
            industry_weight_info = zz1000_sw_weight_and_price_date.groupby('sw_industry_code_1')[['weight','buy_amt']].sum()
            industry_weight_info['yesterday_total_buy'] = yesterday_buy_info_by_ticker.groupby('sw_industry_code_1')['act_buy_amt_t-1'].sum()
            industry_weight_info['yesterday_total_buy'] = industry_weight_info['yesterday_total_buy'].fillna(0)
            industry_weight_info['yesterday_total_sell'] = yesterday_sell_info_by_ticker.groupby('sw_industry_code_1')['act_sell_amt_t-1'].sum()
            industry_weight_info['sell_capacity'] = (industry_weight_info['buy_amt'] - industry_weight_info['yesterday_total_sell']).clip_lower(0)

            industry_weight_info['strategy_allocation'] = industry_weight_info['sell_capacity'] + industry_weight_info['yesterday_total_buy']
            industry_weight_info['strategy_weight'] = industry_weight_info['strategy_allocation'] / industry_weight_info['strategy_allocation'].sum()
            industry_weight_info['t-1_buy_weight'] = industry_weight_info['yesterday_total_buy'] / industry_weight_info['strategy_allocation'].sum()
            industry_weight_info['t_buy_weight'] = 0
            industry_weight_info['t_zz1000_weight'] = industry_weight_info['sell_capacity'] / industry_weight_info['strategy_allocation'].sum()
            industry_weight_info['dt'] = date
            industry_weight_info = industry_weight_info.reset_index()
            industry_weight_info['sw_industry_name_1'] = industry_weight_info['sw_industry_code_1'].map(industry_name_dict)

            day_df_replace_weight.loc[date, '信号端权重'] = industry_weight_info['yesterday_total_buy'].sum() / (industry_weight_info['sell_capacity'].sum() + industry_weight_info['yesterday_total_buy'].sum())
            day_df_industry_weight.append(industry_weight_info[['dt', 'sw_industry_code_1', 'sw_industry_name_1', 'weight','strategy_weight', 't-1_buy_weight', 't_buy_weight', 't_zz1000_weight']])

            yesterday_buy_info_by_ticker = pd.DataFrame({
                'act_buy_amt_t-1': 0,
                'CNLTS_BETA': ZZ1000_sw_weight_and_price.loc[date,'CNLTS_BETA'],
                'CNLTS_LIQUIDTY': ZZ1000_sw_weight_and_price.loc[pd.to_datetime(start_date_), 'CNLTS_LIQUIDTY'],
                'CNLTS_MOMENTUM': ZZ1000_sw_weight_and_price.loc[pd.to_datetime(start_date_), 'CNLTS_MOMENTUM'],
                'CNLTS_RESVOL': df_strategy_sign_sw1.loc[pd.to_datetime(start_date_), 'CNLTS_RESVOL'],
                'CNLTS_SIZE': df_strategy_sign_sw1.loc[pd.to_datetime(start_date_), 'CNLTS_SIZE'],
                'sw_industry_code_1': ZZ1000_sw_weight_and_price.loc[date,'sw_industry_code_1']
            })
            yesterday_sell_info_by_ticker = pd.DataFrame({
                'act_sell_amt_t-1': 0,
                'CNLTS_BETA': ZZ1000_sw_weight_and_price.loc[date,'CNLTS_BETA'],
                'sw_industry_code_1': ZZ1000_sw_weight_and_price.loc[date,'sw_industry_code_1']
            })
            continue
        # 组合的行业每日规模限制
        industry_deviation_up_dict = ZZ1000_groupby_industry.loc[date]['buy_amt_limit'].to_dict()

        # 读取当天zz1000成分股信息
        zz1000_sw_weight_and_price_date = ZZ1000_sw_weight_and_price.loc[date]
        zz1000_sw_weight_and_price_date['act_sell_amt_t-1'] = yesterday_sell_info_by_ticker['act_sell_amt_t-1']
        zz1000_sw_weight_and_price_date[['act_sell_amt_t-1']] = zz1000_sw_weight_and_price_date[['act_sell_amt_t-1']].fillna(0)
        zz1000_sw_weight_and_price_date['sell_capacity'] = (zz1000_sw_weight_and_price_date['buy_amt'] - zz1000_sw_weight_and_price_date['act_sell_amt_t-1']).clip_lower(0)
        sell_capacity_dict = zz1000_sw_weight_and_price_date['sell_capacity'].to_dict()

        df_strategy_sign_sw1_date = df_strategy_sign_sw1.loc[date]

        portfolio_date = pd.concat([df_strategy_sign_sw1_date[['vote_sum_pred','sw_industry_code_1','CNLTS_BETA']],zz1000_sw_weight_and_price_date[['vote_sum_pred','sw_industry_code_1','CNLTS_BETA']]])
        portfolio_date['var'] = portfolio_date.index

        prob = pulp.LpProblem('Determine_Act_Buy_Amt', pulp.LpMaximize)
        buy_vars = pulp.LpVariable.dicts('Buy', portfolio_date['var'], lowBound=0, cat='Continuous')  # 字典，投资组合权重不能为负
        prob += pulp.lpSum([portfolio_date.loc[i, 'vote_sum_pred'] * buy_vars[i] for i in portfolio_date['var']]), 'Total_Signal_Weighted_Buy'

        # 添加约束条件
        for i in portfolio_date['var']:
            if i[1] in ['ceres', 'mimas', 'p4']:
                prob += buy_vars[i] <= 5e6, f'Max_Buy_Sample_{i}'
            elif i[1] == 'saturn':
                prob += buy_vars[i] <= 1e7, f'Max_Buy_Sample_{i}'
            elif i[1] == 'zz1000':
                prob += buy_vars[i] <= sell_capacity_dict[i], f'Max_{i}'
        # 买卖平衡限制
        prob += pulp.lpSum([buy_vars[i] if i in df_strategy_sign_sw1_date.index else (buy_vars[i]-sell_capacity_dict[i]) for i in portfolio_date.index]) == 0

        # 行业偏离度限制
        industries = df_strategy_sign_sw1_date['sw_industry_code_1'].unique() # 信号行业
        for j in industries:
            yesterday_buy_industry = yesterday_buy_info_by_ticker[yesterday_buy_info_by_ticker['sw_industry_code_1'] == j]['act_buy_amt_t-1'].sum()
            indices = df_strategy_sign_sw1_date[df_strategy_sign_sw1_date['sw_industry_code_1'] == j].index
            prob += pulp.lpSum([buy_vars[i] for i in indices]) <= max(0, industry_deviation_up_dict[j] - yesterday_buy_industry), f'Max_Buy_Industry_{j}'

        # beta风格因子限制
        prob += pulp.lpSum([portfolio_date.loc[i,'CNLTS_BETA']*buy_vars[i] for i in portfolio_date['var']]) <= \
                (1+deviation)*ZZ1000_buy_amt_daily-(yesterday_buy_info_by_ticker['act_buy_amt_t-1']*yesterday_buy_info_by_ticker['CNLTS_BETA']).sum(),'Max_Beta'

        # 每日总买入额度限制
        prob += pulp.lpSum([buy_vars[i] for i in df_strategy_sign_sw1_date.index]) <= (ZZ1000_buy_amt_daily - yesterday_buy_info_by_ticker['act_buy_amt_t-1'].sum()), 'Max_Daily_Buy'
        prob.solve()
        if pulp.LpStatus[prob.status] != 'Optimal':
            print(f'求解状态：{pulp.LpStatus[prob.status]}')
            raise Exception('线性规划问题未能找到最优解')
        # 确定买入端
        df_strategy_sign_sw1_date['act_buy_amt'] = [pulp.value(buy_vars[i]) for i in df_strategy_sign_sw1_date.index]
        df_strategy_sign_sw1_date['act_buy_amt'] = df_strategy_sign_sw1_date[['act_buy_amt', 'buy_amt']].min(axis=1) #默认可以买入
        df_strategy_sign_sw1.loc[date]['act_buy_amt'] = df_strategy_sign_sw1_date['act_buy_amt']
        # 当日信号总买入规模
        total_buy = df_strategy_sign_sw1_date['act_buy_amt'].sum()
        # 分行业统计买入规模
        buy_info_by_industry = df_strategy_sign_sw1_date.groupby('sw_industry_code_1')['act_buy_amt'].sum().reset_index()
        buy_info_by_industry.rename(columns={'act_buy_amt': 'total_buy'}, inplace=True)

        # 确定卖出端
        zz1000_sw_weight_and_price_date['act_buy_amt'] = [pulp.value(buy_vars[i]) for i in zz1000_sw_weight_and_price_date.index]
        zz1000_sw_weight_and_price_date['act_sell_amt'] = zz1000_sw_weight_and_price_date['sell_capacity'] - zz1000_sw_weight_and_price_date['act_buy_amt']
        # 实际卖出额度要和实际买入额度一致，不留有敞口
        zz1000_sw_weight_and_price_date['act_sell_amt'] = total_buy*zz1000_sw_weight_and_price_date['act_sell_amt']/zz1000_sw_weight_and_price_date['act_sell_amt'].sum()

        ZZ1000_sw_weight_and_price.loc[date]['act_sell_amt'] = zz1000_sw_weight_and_price_date['act_sell_amt']

        # 统计权重数据
        day_df_replace_weight.loc[date, '剩余现货替换比例'] = total_buy / zz1000_sw_weight_and_price_date['sell_capacity'].sum()
        day_df_replace_weight.loc[date, '信号端权重'] = (total_buy + yesterday_buy_info_by_ticker['act_buy_amt_t-1'].sum()) \
                                                        / (zz1000_sw_weight_and_price_date['sell_capacity'].sum() + yesterday_buy_info_by_ticker['act_buy_amt_t-1'].sum())

        industry_weight_info = zz1000_sw_weight_and_price_date.groupby('sw_industry_code_1')[['weight']].sum()
        industry_weight_info['yesterday_total_buy'] = yesterday_buy_info_by_ticker.groupby('sw_industry_code_1')['act_buy_amt_t-1'].sum()
        industry_weight_info['yesterday_total_buy'] = industry_weight_info['yesterday_total_buy'].fillna(0)
        industry_weight_info['sell_capacity'] = zz1000_sw_weight_and_price_date.groupby('sw_industry_code_1')['sell_capacity'].sum()
        industry_weight_info['total_buy'] = df_strategy_sign_sw1_date.groupby('sw_industry_code_1')['act_buy_amt'].sum()
        industry_weight_info['total_buy'] = industry_weight_info['total_buy'].fillna(0)
        industry_weight_info['total_sell'] = zz1000_sw_weight_and_price_date.groupby('sw_industry_code_1')['act_sell_amt'].sum()

        industry_weight_info['strategy_allocation'] = industry_weight_info['sell_capacity'] + industry_weight_info['yesterday_total_buy'] \
                                                      + industry_weight_info['total_buy'] - industry_weight_info['total_sell']
        industry_weight_info['strategy_weight'] = industry_weight_info['strategy_allocation'] / industry_weight_info['strategy_allocation'].sum()
        industry_weight_info['t-1_buy_weight'] = industry_weight_info['yesterday_total_buy'] / industry_weight_info['strategy_allocation'].sum()
        industry_weight_info['t_buy_weight'] = industry_weight_info['total_buy'] / industry_weight_info['strategy_allocation'].sum()
        industry_weight_info['t_zz1000_weight'] = (industry_weight_info['sell_capacity'] - industry_weight_info['total_sell']) / industry_weight_info['strategy_allocation'].sum()
        industry_weight_info = industry_weight_info.reset_index()
        industry_weight_info['dt'] = date
        industry_weight_info['sw_industry_name_1'] = industry_weight_info['sw_industry_code_1'].map(industry_name_dict)
        day_df_industry_weight.append(industry_weight_info[['dt', 'sw_industry_code_1', 'sw_industry_name_1', 'weight', 'strategy_weight', 't-1_buy_weight','t_buy_weight', 't_zz1000_weight']])

        yesterday_buy_info_by_ticker = df_strategy_sign_sw1_date[['act_buy_amt', 'CNLTS_BETA', 'sw_industry_code_1']].rename(columns={'act_buy_amt': 'act_buy_amt_t-1'})
        yesterday_sell_info_by_ticker = zz1000_sw_weight_and_price_date[['act_sell_amt', 'CNLTS_BETA', 'sw_industry_code_1']].rename(columns={'act_sell_amt': 'act_sell_amt_t-1'})

    day_df_industry_weight = pd.concat(day_df_industry_weight)
    df_strategy_sign_sw1['act_profit'] = df_strategy_sign_sw1['act_buy_amt'] * (df_strategy_sign_sw1['pct'] - 0.004)  # 策略端实际扣费收益

    ZZ1000_sw_weight_and_price['act_profit_0931_next_0931'] = -ZZ1000_sw_weight_and_price['act_sell_amt'] * (ZZ1000_sw_weight_and_price['label_0931_next_0931'] + 0.001)
    ZZ1000_sw_weight_and_price['act_profit_931_941_twap_next_twap'] = -ZZ1000_sw_weight_and_price['act_sell_amt'] * (ZZ1000_sw_weight_and_price['label_931_941_twap_next_twap'] + 0.001)

    # 按日生成回测结果
    day_df_strategy = pd.DataFrame()

    day_df_strategy['000852.SH_label_0931_next_0931'] = index_md_unstack[('label_0931_next_0931', '000852.SH')]
    day_df_strategy['000852.SH_label_931_941_twap_next_twap'] = index_md_unstack[('label_931_941_twap_next_twap', '000852.SH')]  # profit.groupby('dt')['index_pct'].mean() #模拟收益文件中若有指数收益率，以模拟收益文件为主

    day_df_strategy['剩余现货替换比例'] = day_df_replace_weight['剩余现货替换比例']
    day_df_strategy['信号端权重'] = day_df_replace_weight['信号端权重']

    merged_df = ZZ1000_sw_weight_and_price[['act_sell_amt']].reset_index().set_index(['dt','Ticker']).merge(df_strategy_sign_sw1[['act_buy_amt']], left_index=True, right_index=True, how='inner')
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

    day_df_strategy[f'{strategy_join}行业完全对冲信号多头暴露'] = day_df_strategy[f'{strategy_join}行业完全对冲信号实际买入规模'] - ZZ1000_sw_weight_and_price['act_sell_amt'].groupby('dt').sum()

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

    if len(strategy_list)>1:
        for strategy in strategy_list:
            day_df_strategy[f'{strategy}信号样本买入规模'] = df_strategy_sign_sw1[df_strategy_sign_sw1.index.get_level_values(2) == strategy].groupby('dt')['buy_amt'].sum()
            day_df_strategy[f'{strategy}信号样本买入规模'] = day_df_strategy[f'{strategy}信号样本买入规模'].fillna(0)
            day_df_strategy[f'{strategy}指数完全对冲多头暴露'] = 0
            day_df_strategy[f'{strategy}指数收益'] = -day_df_strategy[f'{strategy}信号样本买入规模'] * day_df_strategy['000852.SH_label_931_941_twap_next_twap']
            day_df_strategy[f'{strategy}原信号'] = df_strategy_sign_sw1[df_strategy_sign_sw1.index.get_level_values(2) == strategy].groupby('dt')['profit'].sum()
            day_df_strategy[f'{strategy}原信号'] = day_df_strategy[f'{strategy}原信号'].fillna(0)
            day_df_strategy[f'{strategy}指数完全对冲'] = day_df_strategy[f'{strategy}原信号'] + day_df_strategy[f'{strategy}指数收益']

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