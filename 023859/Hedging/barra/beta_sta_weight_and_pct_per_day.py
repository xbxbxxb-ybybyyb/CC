import pandas as pd
import barra_util as util
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()
import itertools
import os

start_date, end_date = 20210701, 20220630
trading_days = s.tradingday(start_date, end_date)

root_dict = {'index_info':'/data/user/023859/Hedging/index_price_20210701_20240630.pkl',\
             'zz1000_info':'/data/user/023859/Hedging/ZZ1000_sw_weight_and_price_beta_20210701_20240630.pkl',\
             'strategy_info':'/data/user/023859/Hedging/saturn+ceres+mimas+p4/df_strategy_basic_sw1_beta_20210701_20220630.pkl',\
             'saturn_profit_info':'/data/group/800463/sunss/saturn/profit/20241129/p2_profit_interval_s1_0.10_0.10_1000_1500_250_20.h5',\
             'mimas_profit_info':'/data/group/800463/sunss/mimas/profit/20241225/p2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',\
             'ceres_profit_info':'/data/group/800463/sunss/ceres/profit/20241225/sp2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',\
             'p4_profit_info':'/data/group/800463/sunss/p4/profit/20241225/p4_profit_interval_s1_0.10_0.10_500_1500_250_20.h5'}

strategy_list = ['saturn', 'ceres', 'mimas', 'p4']
# strategy_list = ['ceres', 'mimas', 'p4']

strategy_join = '+'.join(strategy_list)
ZZ1000_amt = 2
industry_deviation = 1.5
vote_num_list = [4,3,2]
tables_weight_by_date_industry = {}
tables_weight_by_date = {}

for vote_num in vote_num_list:
    day_df_strategy, day_df_industry_weight, df_strategy_sign_sw1, ZZ1000_sw_weight_and_price = util.calc_profit(trading_days, strategy_list, root_dict, ZZ1000_amt*1e8, industry_deviation, vote_num)
    ZZ1000_sw_weighted_return = ZZ1000_sw_weight_and_price.groupby(['dt', 'sw_industry_code_1', 'sw_industry_name_1']).apply(lambda x: (x['weight'] * x['label_931_941_twap_next_twap']).sum() / x['weight'].sum()).to_frame(name='成分股加权收益率')
    ZZ1000_sw_weighted_return = ZZ1000_sw_weighted_return.reset_index().rename(columns={'dt': '日期', 'sw_industry_code_1': '行业代码', 'sw_industry_name_1': '行业名称'}).set_index(['日期', '行业代码', '行业名称'])
    df_strategy_basic = pd.read_pickle(root_dict['strategy_info'])
    df_strategy_basic = df_strategy_basic[df_strategy_basic['strategy'].isin(strategy_list)]
    df_strategy_basic = df_strategy_basic.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
    df_strategy_sign = df_strategy_basic[df_strategy_basic['vote_sum_pred'] >= vote_num]

    df_strategy_sign_buy_amt = df_strategy_sign.groupby(['dt', 'sw_industry_code_1', 'sw_industry_name_1'])[['buy_amt']].sum()

    day_df_industry_weight_ = day_df_industry_weight.reset_index(drop=True)
    day_df_industry_weight_ = day_df_industry_weight_.set_index(['dt', 'sw_industry_code_1', 'sw_industry_name_1'])

    day_df_industry_weight_[f'{strategy_join}_original_weight'] = df_strategy_sign_buy_amt['buy_amt'] / df_strategy_sign_buy_amt.groupby('dt')['buy_amt'].transform('sum')
    day_df_industry_weight_[f'{strategy_join}_original_weight'] = day_df_industry_weight_[f'{strategy_join}_original_weight'].fillna(0)

    rename_dict = {'dt':'日期', 'sw_industry_code_1':'行业代码', 'sw_industry_name_1':'行业名称','weight':'原始权重','strategy_weight':f'{strategy_join}配置权重', \
                   't-1_buy_weight': f'{strategy_join}_t-1日信号买入权重','t_buy_weight': f'{strategy_join}_t日信号买入权重','t_zz1000_weight': f'{strategy_join}_t日剩余现货权重',\
                   f'{strategy_join}_original_weight':f'{strategy_join}原信号权重'}
    strategy_sort_list = []
    for strategy in strategy_list:
        strategy_sort_list += [f'{strategy}原信号权重',f'{strategy}信号数量']
        strategy_basic_df = df_strategy_basic[df_strategy_basic['strategy'] == strategy]
        strategy_sign_df = df_strategy_sign[df_strategy_sign['strategy'] == strategy]
        strategy_sign_buy_amt = strategy_sign_df.groupby(['dt', 'sw_industry_code_1', 'sw_industry_name_1'])[['buy_amt']].sum()
        strategy_basic_pct = strategy_basic_df.groupby(['dt', 'sw_industry_code_1', 'sw_industry_name_1'])[['pct']].mean()
        strategy_sign_pct = strategy_sign_df.groupby(['dt', 'sw_industry_code_1', 'sw_industry_name_1'])[['pct']].mean()

        day_df_industry_weight_[f'{strategy}_basic_pct'] = strategy_basic_pct
        day_df_industry_weight_[f'{strategy}_sign_pct'] = strategy_sign_pct
        day_df_industry_weight_[f'{strategy}_original_weight'] = strategy_sign_buy_amt['buy_amt'] / strategy_sign_buy_amt.groupby('dt')['buy_amt'].transform('sum')
        day_df_industry_weight_[f'{strategy}_original_weight'] = day_df_industry_weight_[f'{strategy}_original_weight'].fillna(0)

        day_df_industry_weight_[f'{strategy}_sample_count'] = strategy_sign_df.groupby(['dt', 'sw_industry_code_1', 'sw_industry_name_1'])['vote_sum_pred'].count()
        day_df_industry_weight_[f'{strategy}_sample_count'] = day_df_industry_weight_[f'{strategy}_sample_count'].fillna(0)

        rename_dict.update({f'{strategy}_basic_pct':f'{strategy}基础样本收益率',f'{strategy}_sign_pct':f'{strategy}信号样本收益率',\
                            f'{strategy}_original_weight': f'{strategy}原信号权重',f'{strategy}_sample_count': f'{strategy}信号数量'})


    day_df_industry_weight_ = day_df_industry_weight_.reset_index().rename(columns=rename_dict).set_index(['日期', '行业代码', '行业名称'])
    day_df_industry_weight_ = day_df_industry_weight_.groupby(level='日期', group_keys=False).apply(lambda x: x.sort_values(strategy_sort_list+[f'{strategy_join}配置权重',f'{strategy_join}_t-1日信号买入权重',f'{strategy_join}_t日信号买入权重',f'{strategy_join}_t日剩余现货权重','原始权重'], ascending=False))
    day_df_industry_weight_ = pd.concat([ZZ1000_sw_weighted_return, day_df_industry_weight_], axis=1)
    tables_weight_by_date_industry[f'vote>={vote_num}'] = day_df_industry_weight_
    tables_weight_by_date[f'vote>={vote_num}'] = day_df_strategy[['信号端权重','剩余现货替换比例','zz1000成分股权重']]

folder_name = f'/dfs/user/023859/share_file/for_wys/industry_hedging/{strategy_join}/beta'
os.makedirs(folder_name, exist_ok=True)

with pd.ExcelWriter(folder_name+f'/每日行业收益率及权重统计_{ZZ1000_amt}_{industry_deviation}_{start_date}_{end_date}.xlsx', engine='openpyxl') as writer:
    # 将每个DataFrame写入到不同的sheet
    for sheet_name, df in tables_weight_by_date_industry.items():
        df1 = df.drop(columns = ['原始权重',f'{strategy_join}配置权重',f'{strategy_join}_t-1日信号买入权重',f'{strategy_join}_t日信号买入权重',f'{strategy_join}_t日剩余现货权重','成分股加权收益率'])
        df1 = df1[[f'{strategy}基础样本收益率' for strategy in strategy_list]+[f'{strategy}信号样本收益率' for strategy in strategy_list]+[f'{strategy_join}原信号权重']+([f'{strategy}原信号权重' for strategy in strategy_list] if len(strategy_list)>1 else [])+[f'{strategy}信号数量' for strategy in strategy_list]]
        columns_list = list(itertools.product(['基础样本收益率','信号样本收益率','原信号权重','信号数量'],strategy_list))
        if len(strategy_list)>1:
            columns_list.insert(columns_list.index(('原信号权重', strategy_list[0])), ('原信号权重', f'{strategy_join}'))
        df1.columns = pd.MultiIndex.from_tuples(columns_list)
        df1[['原始权重',f'{strategy_join}配置权重',f'{strategy_join}_t-1日信号买入权重',f'{strategy_join}_t日信号买入权重',f'{strategy_join}_t日剩余现货权重','成分股加权收益率']] = \
        df[['原始权重',f'{strategy_join}配置权重',f'{strategy_join}_t-1日信号买入权重',f'{strategy_join}_t日信号买入权重',f'{strategy_join}_t日剩余现货权重','成分股加权收益率']]
        df1 = df1[['原始权重',f'{strategy_join}配置权重',f'{strategy_join}_t-1日信号买入权重',f'{strategy_join}_t日信号买入权重',f'{strategy_join}_t日剩余现货权重','原信号权重','信号数量','成分股加权收益率','基础样本收益率','信号样本收益率']]
        df1.to_excel(writer, sheet_name=sheet_name)

with pd.ExcelWriter(folder_name+f'/每日行业对冲信号端权重及zz1000成分股权重_{ZZ1000_amt}_{industry_deviation}_{start_date}_{end_date}.xlsx', engine='openpyxl') as writer:
    # 将每个DataFrame写入到不同的sheet
    for sheet_name, df in tables_weight_by_date.items():
        df.to_excel(writer, sheet_name=sheet_name)