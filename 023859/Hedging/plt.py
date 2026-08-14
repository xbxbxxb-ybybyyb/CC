import pandas as pd
import industry_hedging_utilities as util
from xquant.factordata import FactorData
s = FactorData()
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体，适用于 Windows
rcParams['axes.unicode_minus'] = False

start_date, end_date = 20210701, 20230630
trading_days = s.tradingday(start_date, end_date)
root_dict = {'index_info':'/data/user/023859/Hedging/index_price_20210701_20240630.pkl',\
             'zz1000_info':'/dfs/user/023859/industry_hedging/ZZ1000_sw_weight_and_price_20210701_20240630.pkl',\
             'strategy_info':f'/dfs/user/023859/industry_hedging/saturn+ceres+mimas+p4/df_strategy_basic_sw1_{start_date}_{end_date}.pkl',\
             'saturn_profit_info':'/data/group/800463/sunss/saturn/profit/20241129/p2_profit_interval_s1_0.10_0.10_1000_1500_250_20.h5',\
             'mimas_profit_info':'/data/group/800463/sunss/mimas/profit/20241225/p2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',\
             'ceres_profit_info':'/data/group/800463/sunss/ceres/profit/20241225/sp2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',\
             'p4_profit_info':'/data/group/800463/sunss/p4/profit/20241225/p4_profit_interval_s1_0.10_0.10_500_1500_250_20.h5'}

strategy_list = ['mimas']
strategy_join = '+'.join(strategy_list)

for _ in range(1):
    day_df_strategy, _,_,_ = util.calc_profit(trading_days,strategy_list,root_dict,3e8,[1.5,0.02])

    day_df_strategy[f'{strategy_join}原信号最大回撤'] = (day_df_strategy[f'{strategy_join}原信号'].cumsum().cummax() - day_df_strategy[f'{strategy_join}原信号'].cumsum())
    day_df_strategy[f'{strategy_join}行业完全对冲信号端最大回撤'] = (day_df_strategy[f'{strategy_join}行业完全对冲信号端'].cumsum().cummax() - day_df_strategy[f'{strategy_join}行业完全对冲信号端'].cumsum())
    day_df_strategy[f'{strategy_join}行业完全对冲最大回撤'] = (day_df_strategy[f'{strategy_join}行业完全对冲'].cumsum().cummax() - day_df_strategy[f'{strategy_join}行业完全对冲'].cumsum())

    time_list = day_df_strategy.index
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 15))

    ax1.plot(time_list, day_df_strategy[f'{strategy_join}原信号'].cumsum(), color='blue', label=f'{strategy_join}原信号')
    ax1.plot(time_list, day_df_strategy[f'{strategy_join}行业完全对冲信号端'].cumsum(), color='green',label=f'{strategy_join}行业完全对冲信号端')
    ax1.plot(time_list, day_df_strategy[f'{strategy_join}行业完全对冲'].cumsum(), color='purple',label=f'{strategy_join}行业完全对冲')

    ax1.set_xlabel('日期')
    ax1.set_ylabel('策略收益', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.legend(loc='upper center')

    ax1_2 = ax1.twinx()
    ax1_2.plot(time_list, day_df_strategy[f'{strategy_join}行业收益'].cumsum(), color='red',label=f'{strategy_join}对冲端收益')
    ax1_2.set_ylabel('对冲端收益')
    ax1_2.legend(loc='center right')

    ax1.set_title('收益曲线')

    ax2.plot(time_list, day_df_strategy[f'{strategy_join}原信号最大回撤'], color='blue',label=f'{strategy_join}原信号最大回撤')
    ax2.plot(time_list, day_df_strategy[f'{strategy_join}行业完全对冲信号端最大回撤'], color='green',label=f'{strategy_join}行业完全对冲信号端最大回撤')
    ax2.plot(time_list, day_df_strategy[f'{strategy_join}行业完全对冲最大回撤'], color='purple',label=f'{strategy_join}行业完全对冲最大回撤')

    ax2.set_title('回撤曲线')
    ax2.set_xlabel('日期')
    ax2.set_ylabel('回撤')
    ax2.legend(loc='upper left')
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(f'/dfs/user/023859/industry_hedging/{strategy_join}/neutral_vote.png')  # 保存为PNG格式
    plt.show()

    day_df_strategy.loc[pd.to_datetime('20210701'):pd.to_datetime('20211231'), 'period'] = 1
    day_df_strategy.loc[pd.to_datetime('20220101'):pd.to_datetime('20220630'), 'period'] = 2
    day_df_strategy.loc[pd.to_datetime('20220701'):pd.to_datetime('20221231'), 'period'] = 3
    day_df_strategy.loc[pd.to_datetime('20230101'):pd.to_datetime('20230630'), 'period'] = 4
    # day_df_strategy.loc[pd.to_datetime('20230701'):pd.to_datetime('20231231'),'period']=5
    # day_df_strategy.loc[pd.to_datetime('20240101'):pd.to_datetime('20240630'),'period']=6

    periods = day_df_strategy['period'].unique()
    fig, axes = plt.subplots(2, 2, figsize=(20, 8))
    for ax1, period in zip(axes.ravel(), periods):
        data_period = day_df_strategy[day_df_strategy['period'] == period]

        time_list = data_period.index
        ax1.plot(time_list, data_period[f'{strategy_join}原信号'].cumsum(), color='blue', label=f'{strategy_join}原信号')
        ax1.plot(time_list, data_period[f'{strategy_join}行业完全对冲信号端'].cumsum(), color='green', label=f'{strategy_join}行业完全对冲信号端')
        ax1.plot(time_list, data_period[f'{strategy_join}行业完全对冲'].cumsum(), color='purple', label=f'{strategy_join}行业完全对冲')

        ax1.set_xlabel('日期')
        ax1.set_ylabel('策略收益', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.legend(loc='upper center')

        ax1_2 = ax1.twinx()
        ax1_2.plot(time_list, data_period[f'{strategy_join}行业收益'].cumsum(), color='red', label=f'{strategy_join}对冲端收益')
        ax1_2.set_ylabel('对冲端收益')
        ax1_2.legend(loc='lower center')

        ax1.set_title('收益曲线')

    plt.tight_layout()
    plt.savefig(f'/dfs/user/023859/industry_hedging/{strategy_join}/neutral_vote_period.png')  # 保存为PNG格式
    plt.show()

