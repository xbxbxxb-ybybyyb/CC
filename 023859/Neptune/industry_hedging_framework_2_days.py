import pandas as pd
import industry_hedging_utilities as util
from multiprocessing import Pool
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()
import pickle

start_date, end_date = 20220701, 20221231
trading_days = s.tradingday(start_date, end_date)
vote_num_list = [4,3,2]

print('交易日个数：%s'%(len(trading_days)))


strategy_list = ['ceres','mimas','p4']
zz1000_amt_dict = {'1亿现货':1e8,'2亿现货':2e8, '3亿现货':3e8}
deviation_dict = {'行业偏离度1':1,'行业偏离度1.5':1.5}

root_dict = {'index_info':'/data/user/023859/Hedging/index_price_20210701_20240630.pkl',\
             'zz1000_info':'/data/user/023859/Hedging/ZZ1000_sw_weight_and_price_20210701_20240630.pkl',\
             'strategy_info':'/data/user/023859/Hedging/ceres+mimas+p4/df_strategy_basic_sw1_20220701_20221231.pkl',\
             # 'saturn_profit_info':'/data/group/800463/sunss/saturn/profit/20241129/p2_profit_interval_s1_0.10_0.10_1000_1500_250_20.h5',\
             'mimas_profit_info':'/data/group/800463/sunss/mimas/profit/20241225/p2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',\
             'ceres_profit_info':'/data/group/800463/sunss/ceres/profit/20241225/sp2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',\
             'p4_profit_info':'/data/group/800463/sunss/p4/profit/20241225/p4_profit_interval_s1_0.10_0.10_500_1500_250_20.h5'}

strategy_join = '+'.join(strategy_list)

if len(strategy_list)>1:
    res_list = [f'{strategy_join}原信号'] + [f'{strategy}原信号' for strategy in strategy_list] + [f'{strategy_join}行业完全对冲信号端'] + \
               [f'{strategy_join}指数完全对冲'] + [f'{strategy}指数完全对冲' for strategy in strategy_list] + [f'{strategy_join}行业完全对冲']

    strategy_buy_amt_dict = {f'{strategy_join}原信号':f'{strategy_join}信号样本买入规模',f'{strategy_join}指数完全对冲':f'{strategy_join}信号样本买入规模',\
                             f'{strategy_join}行业完全对冲信号端':f'{strategy_join}行业完全对冲信号实际买入规模',f'{strategy_join}行业完全对冲':f'{strategy_join}行业完全对冲信号实际买入规模'}
    strategy_long_exposure_dict = {f'{strategy_join}原信号':f'{strategy_join}信号样本买入规模',f'{strategy_join}指数完全对冲':f'{strategy_join}指数完全对冲多头暴露',\
                                   f'{strategy_join}行业完全对冲信号端':f'{strategy_join}行业完全对冲信号实际买入规模',f'{strategy_join}行业完全对冲':f'{strategy_join}行业完全对冲信号多头暴露'}
    for strategy in strategy_list:
        strategy_buy_amt_dict.update({f'{strategy}原信号': f'{strategy}信号样本买入规模',f'{strategy}指数完全对冲': f'{strategy}信号样本买入规模'})
        strategy_long_exposure_dict.update({f'{strategy}原信号': f'{strategy}信号样本买入规模',f'{strategy}指数完全对冲': f'{strategy}指数完全对冲多头暴露'})
else:
    strategy = strategy_list[0]
    res_list = [f'{strategy}原信号',f'{strategy}行业完全对冲信号端',f'{strategy}指数完全对冲',f'{strategy}行业完全对冲']
    strategy_buy_amt_dict = {f'{strategy}原信号':f'{strategy}信号样本买入规模',f'{strategy}指数完全对冲':f'{strategy}信号样本买入规模',\
                             f'{strategy}行业完全对冲信号端':f'{strategy}行业完全对冲信号实际买入规模',f'{strategy}行业完全对冲':f'{strategy}行业完全对冲信号实际买入规模'}
    strategy_long_exposure_dict = {f'{strategy}原信号':f'{strategy}信号样本买入规模',f'{strategy}指数完全对冲':f'{strategy}指数完全对冲多头暴露',\
                                   f'{strategy}行业完全对冲信号端':f'{strategy}行业完全对冲信号实际买入规模',f'{strategy}行业完全对冲':f'{strategy}行业完全对冲信号多头暴露'}



def calc_res(trading_days, strategy_list, root_dict, zz1000_amt_dict, deviation_dict, vote_num):
    sta_df_deviation = pd.DataFrame()
    sta_period = pd.DataFrame()
    for ZZ1000_buy_amt in zz1000_amt_dict.keys():
        for deviation in deviation_dict.keys():
            day_df_strategy, _, _, _ = util.calc_profit(trading_days,strategy_list,root_dict,zz1000_amt_dict[ZZ1000_buy_amt],deviation_dict[deviation],vote_num)
            # day_df_strategy.loc[pd.to_datetime('20210701'):pd.to_datetime('20211231'), 'period'] = 1
            # day_df_strategy.loc[pd.to_datetime('20220101'):pd.to_datetime('20220630'), 'period'] = 2
            day_df_strategy.loc[pd.to_datetime('20220701'):pd.to_datetime('20221231'), 'period'] = 3
            # day_df_strategy.loc[pd.to_datetime('20230101'):pd.to_datetime('20230630'), 'period'] = 4
            # day_df_strategy.loc[pd.to_datetime('20230701'):pd.to_datetime('20231231'), 'period'] = 5
            # day_df_strategy.loc[pd.to_datetime('20240101'):pd.to_datetime('20240630'), 'period'] = 6
            for strategy in res_list:
                sta_df_deviation[(strategy, ZZ1000_buy_amt, deviation)] = util.sta_profit(day_df_strategy[strategy],day_df_strategy[strategy_buy_amt_dict[strategy]],day_df_strategy[strategy_long_exposure_dict[strategy]])
                for period in day_df_strategy['period'].unique():
                    sta_period[(strategy, ZZ1000_buy_amt, deviation, period)] = util.sta_profit(
                        day_df_strategy.loc[day_df_strategy['period'] == period, strategy], \
                        day_df_strategy.loc[day_df_strategy['period'] == period, strategy_buy_amt_dict[strategy]], \
                        day_df_strategy.loc[day_df_strategy['period'] == period, strategy_long_exposure_dict[strategy]])
    sta_df_deviation = sta_df_deviation.T
    sta_df_deviation.index = pd.MultiIndex.from_tuples(list(sta_df_deviation.index))
    sta_df_deviation = sta_df_deviation.sort_index()
    if len(strategy_list)>1:
        strategies_to_duplicate = [f'{strategy_join}原信号'] + [f'{strategy}原信号' for strategy in strategy_list] + [f'{strategy_join}指数完全对冲'] + [f'{strategy}指数完全对冲' for strategy in strategy_list]
    else:
        strategies_to_duplicate = [f'{strategy_join}原信号',f'{strategy_join}指数完全对冲']

    sta_df_to_duplicate = sta_df_deviation[sta_df_deviation.index.get_level_values(0).isin(strategies_to_duplicate)]
    df_other = sta_df_deviation[~sta_df_deviation.index.get_level_values(0).isin(strategies_to_duplicate)]
    sta_df_to_duplicate = sta_df_to_duplicate.groupby(level=0).first()
    sta_df_to_duplicate = sta_df_to_duplicate.reindex(strategies_to_duplicate)
    extra_index = pd.MultiIndex.from_product([sta_df_to_duplicate.index, ['-'], ['-']])
    sta_df_to_duplicate_multi = sta_df_to_duplicate.set_index([extra_index.get_level_values(0), extra_index.get_level_values(1), extra_index.get_level_values(2)])
    sta_df_deviation = pd.concat([sta_df_to_duplicate_multi, df_other])

    sta_period = sta_period.T
    sta_period.index = pd.MultiIndex.from_tuples(list(sta_period.index))
    sta_period = sta_period.sort_index()
    period_df_to_duplicate = sta_period[sta_period.index.get_level_values(0).isin(strategies_to_duplicate)]
    period_df_other = sta_period[~sta_period.index.get_level_values(0).isin(strategies_to_duplicate)]
    period_df_to_duplicate = period_df_to_duplicate.groupby(level=[0, 3]).first()
    period_df_to_duplicate = period_df_to_duplicate.reindex(strategies_to_duplicate, level=0)
    period_extra_index = pd.MultiIndex.from_product([period_df_to_duplicate.index.levels[0], ['-'], ['-'], period_df_to_duplicate.index.levels[1]])
    period_df_to_duplicate_multi = period_df_to_duplicate.set_index(
        [period_extra_index.get_level_values(0), period_extra_index.get_level_values(1),
         period_extra_index.get_level_values(2), period_extra_index.get_level_values(3)])
    sta_period = pd.concat([period_df_to_duplicate_multi, period_df_other])

    sta_period1 = sta_period.groupby(level=[0, 1, 2], sort=False).mean()

    return sta_df_deviation, sta_period, sta_period1

with Pool(processes=3) as pool:
    results = pool.starmap(calc_res,[(trading_days, strategy_list, root_dict, zz1000_amt_dict, deviation_dict, vote_num) for vote_num in vote_num_list])

for i in range(len(vote_num_list)):
    vote_num = vote_num_list[i]
    sta_df_deviation = results[i][0]
    sta_period = results[i][1]
    sta_period1 = results[i][2]
    excel_writer = pd.ExcelWriter(f'/data/user/023859/Hedging/industry/industry_neutral/{strategy_join}_vote{vote_num}_行业中性对冲回测结果{start_date}_{end_date}.xlsx')
    sta_df_deviation.to_excel(excel_writer, sheet_name='sta_df_deviation')
    sta_period.to_excel(excel_writer, sheet_name='sta_period')
    sta_period1.to_excel(excel_writer, sheet_name='sta_period1')
    excel_writer.save()