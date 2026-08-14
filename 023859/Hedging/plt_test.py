import industry_hedging_utilities as util
from xquant.factordata import FactorData
s = FactorData()
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体，适用于 Windows
rcParams['axes.unicode_minus'] = False

start_date, end_date = 20220701, 20221231
trading_days = s.tradingday(start_date, end_date)
strategy_list = ['p4']
root_dict = {'index_info':'/data/user/023859/Hedging/index_price_20210701_20240630.pkl',\
             'zz1000_info':'/data/user/023859/Hedging/ZZ1000_sw_weight_and_price_20210701_20240630.pkl',\
             'strategy_info':'/data/user/023859/Hedging/p4/df_strategy_basic_sw1_20220701_20221231.pkl', \
             # 'saturn_profit_info': '/data/group/800463/sunss/saturn/profit/20241129/p2_profit_interval_s1_0.10_0.10_1000_1500_250_20.h5', \
             # 'mimas_profit_info':'/data/group/800463/sunss/mimas/profit/20241225/p2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',\
             # 'ceres_profit_info':'/data/group/800463/sunss/ceres/profit/20241225/sp2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5'}
             'p4_profit_info':'/data/group/800463/sunss/p4/profit/20241225/p4_profit_interval_s1_0.10_0.10_500_1500_250_20.h5'}

for vote_num in [4,3,2]:
    day_df_strategy, _,_,_ = util.calc_profit(trading_days,strategy_list,root_dict,1e8,1.5,vote_num)

    day_df_strategy['p4原信号最大回撤'] = (day_df_strategy['p4原信号'].cumsum().cummax() - day_df_strategy['p4原信号'].cumsum())
    day_df_strategy['p4行业完全对冲信号端最大回撤'] = (day_df_strategy['p4行业完全对冲信号端'].cumsum().cummax() - day_df_strategy['p4行业完全对冲信号端'].cumsum())
    day_df_strategy['p4行业完全对冲最大回撤'] = (day_df_strategy['p4行业完全对冲'].cumsum().cummax() - day_df_strategy['p4行业完全对冲'].cumsum())

    time_list = day_df_strategy.index
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 15))

    ax1.plot(time_list, day_df_strategy['p4原信号'].cumsum(), color='blue', label='p4原信号')
    ax1.plot(time_list, day_df_strategy['p4行业完全对冲信号端'].cumsum(), color='green',label='p4行业完全对冲信号端')
    ax1.plot(time_list, day_df_strategy['p4行业完全对冲'].cumsum(), color='purple',label='p4行业完全对冲')

    ax1.set_xlabel('日期')
    ax1.set_ylabel('策略收益', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.legend(loc='upper center')

    ax1_2 = ax1.twinx()
    ax1_2.plot(time_list, day_df_strategy['p4行业收益'].cumsum(), color='red',label='p4对冲端收益')
    ax1_2.set_ylabel('对冲端收益')
    ax1_2.legend(loc='center right')

    ax1.set_title('收益曲线')

    ax2.plot(time_list, day_df_strategy['p4原信号最大回撤'], color='blue',label='p4原信号最大回撤')
    ax2.plot(time_list, day_df_strategy['p4行业完全对冲信号端最大回撤'], color='green',label='p4行业完全对冲信号端最大回撤')
    ax2.plot(time_list, day_df_strategy['p4行业完全对冲最大回撤'], color='purple',label='p4行业完全对冲最大回撤')

    ax2.set_title('回撤曲线')
    ax2.set_xlabel('日期')
    ax2.set_ylabel('回撤')
    ax2.legend(loc='upper left')
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(f'/dfs/user/023859/Hedging/p4/p4_neutral_vote{vote_num}.png')  # 保存为PNG格式
    plt.show()