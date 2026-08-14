import pandas as pd
import os
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()

strategy_version = 20250609
start_date, end_date = 20170110,20240630
test_end_date = 20231231

trading_days = s.tradingday(start_date, end_date)

ZZ1000_weight = []
for date in tqdm(trading_days):
    df_ZZ1000 = s.hset('INDEX',date,'ZZ1000',weightType=1) # 选择预估权重，避免回测用到未来数据
    ZZ1000_weight_date = pd.DataFrame(index = df_ZZ1000['stock'])
    ZZ1000_weight_date.index.names = ['stock']
    ZZ1000_weight_date['weight'] = df_ZZ1000.set_index('stock')['weight']/100
    ZZ1000_weight_date = ZZ1000_weight_date.reset_index()
    ZZ1000_weight_date['dt'] = pd.Timestamp(date)
    ZZ1000_weight_date = ZZ1000_weight_date.rename(columns={'stock':'Ticker'})
    ZZ1000_weight_date = ZZ1000_weight_date.set_index(['dt','Ticker'])[['weight']]
    ZZ1000_weight.append(ZZ1000_weight_date)

ZZ1000_weight = pd.concat(ZZ1000_weight, axis=0)

factor_bank_inf = pd.read_excel(f'/data/group/800463/tangsq/neptune/{strategy_version}/20170110_20221231/factor_bank_inf_sc.xlsx')
strategy_path = f'/dfs/user/023859/neptune/{strategy_version}'
factor_df_path = os.path.join(strategy_path, f'factor_df_sc_20170110_20240630.pkl')

share_file_path_public = f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}'
os.makedirs(share_file_path_public, exist_ok=True)
# share_file_path = f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}'
# os.makedirs(share_file_path, exist_ok=True)

label_path = '/data/user/021012/团队分享/for_tsq/neptune/profit_backtest/2017_2024'
long_term_name = 'p2_profit_intervalTwap_1430_1440_Sell_intervalTwap_1430_1440_0.10_0.10.h5'
mid_term_name = 'p2_profit_intervalTwap_1430_1440_Sell_intervalTwap_1000_1010_0.10_0.10.h5'
short_term_name = 'p2_profit_intervalTwap_1430_1440_Sell_intervalTwap_931_941_0.10_0.10.h5'

label_df_long_term = pd.read_hdf(os.path.join(label_path,long_term_name))
label_df_mid_term = pd.read_hdf(os.path.join(label_path,mid_term_name))
label_df_short_term = pd.read_hdf(os.path.join(label_path,short_term_name))

factor_df_all = pd.read_pickle(factor_df_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
factor_df_all['weight'] = ZZ1000_weight['weight']
factor_df_all['label_pct_long_term'] = label_df_long_term['pct']
factor_df_all['label_pct_mid_term'] = label_df_mid_term['pct']
factor_df_all['label_pct_short_term'] = label_df_short_term['pct']
factor_df_all = factor_df_all.dropna(subset = ['label_pct_long_term','label_pct_mid_term','label_pct_short_term'])

# 保留13位有效数字
mm=factor_df_all.abs().max()
print(mm[mm>1e15])
for col in tqdm(factor_bank_inf['factor_name'].to_list()):
    # if col not in ['zwh_20240201_001','qyh_neptune_20250327_31']:
    factor_df_all[col]=factor_df_all[col].round(13)

assert len(factor_df_all) == len(factor_df_all.dropna())

# 全样本filter: 剔除波动率小于阈值，权重小于万5的样本
volatility_threshold_long_term = factor_df_all.loc[:pd.Timestamp('20201231')]['tsq_newneptune_sc_scene_volatility_long_term'].quantile(0.1)
volatility_threshold_mid_term = factor_df_all.loc[:pd.Timestamp('20201231')]['tsq_newneptune_sc_scene_volatility_mid_term'].quantile(0.1)
volatility_threshold_short_term = factor_df_all.loc[:pd.Timestamp('20201231')]['tsq_newneptune_sc_scene_volatility_short_term'].quantile(0.1)

factor_df_all = factor_df_all[factor_df_all['weight'] >= 0.0005]
factor_df_all_long_term = factor_df_all[factor_df_all['tsq_newneptune_sc_scene_volatility_long_term'] >= max(0.003,volatility_threshold_long_term)]
factor_df_all_mid_term = factor_df_all[factor_df_all['tsq_newneptune_sc_scene_volatility_mid_term'] >= max(0.003,volatility_threshold_mid_term)]
factor_df_all_short_term = factor_df_all[factor_df_all['tsq_newneptune_sc_scene_volatility_short_term'] >= max(0.003,volatility_threshold_short_term)]

# 振幅分场景
swing_median_long_term = factor_df_all_long_term.loc[:pd.Timestamp('20190630')]['tsq_newneptune_sc_scene_swing_long_term'].median()
factor_df_swing_high_long_term = factor_df_all_long_term[factor_df_all_long_term['tsq_newneptune_sc_scene_swing_long_term'] >= swing_median_long_term]
factor_df_swing_low_long_term = factor_df_all_long_term[factor_df_all_long_term['tsq_newneptune_sc_scene_swing_long_term'] < swing_median_long_term]

swing_median_mid_term = factor_df_all_mid_term.loc[:pd.Timestamp('20190630')]['tsq_newneptune_sc_scene_swing_mid_term'].median()
factor_df_swing_high_mid_term = factor_df_all_mid_term[factor_df_all_mid_term['tsq_newneptune_sc_scene_swing_mid_term'] >= swing_median_mid_term]
factor_df_swing_low_mid_term = factor_df_all_mid_term[factor_df_all_mid_term['tsq_newneptune_sc_scene_swing_mid_term'] < swing_median_mid_term]

swing_median_short_term = factor_df_all_short_term.loc[:pd.Timestamp('20190630')]['tsq_newneptune_sc_scene_swing_short_term'].median()
factor_df_swing_high_short_term = factor_df_all_short_term[factor_df_all_short_term['tsq_newneptune_sc_scene_swing_short_term'] >= swing_median_short_term]
factor_df_swing_low_short_term = factor_df_all_short_term[factor_df_all_short_term['tsq_newneptune_sc_scene_swing_short_term'] < swing_median_short_term]

# 波动率分场景
volatility_median_long_term = factor_df_all_long_term.loc[:pd.Timestamp('20190630')]['tsq_newneptune_sc_scene_volatility_long_term'].median()
factor_df_volatility_high_long_term = factor_df_all_long_term[factor_df_all_long_term['tsq_newneptune_sc_scene_volatility_long_term'] >= volatility_median_long_term]
factor_df_volatility_low_long_term = factor_df_all_long_term[factor_df_all_long_term['tsq_newneptune_sc_scene_volatility_long_term'] < volatility_median_long_term]

volatility_median_mid_term = factor_df_all_mid_term.loc[:pd.Timestamp('20190630')]['tsq_newneptune_sc_scene_volatility_mid_term'].median()
factor_df_volatility_high_mid_term = factor_df_all_mid_term[factor_df_all_mid_term['tsq_newneptune_sc_scene_volatility_mid_term'] >= volatility_median_mid_term]
factor_df_volatility_low_mid_term = factor_df_all_mid_term[factor_df_all_mid_term['tsq_newneptune_sc_scene_volatility_mid_term'] < volatility_median_mid_term]

volatility_median_short_term = factor_df_all_short_term.loc[:pd.Timestamp('20190630')]['tsq_newneptune_sc_scene_volatility_short_term'].median()
factor_df_volatility_high_short_term = factor_df_all_short_term[factor_df_all_short_term['tsq_newneptune_sc_scene_volatility_short_term'] >= volatility_median_short_term]
factor_df_volatility_low_short_term = factor_df_all_short_term[factor_df_all_short_term['tsq_newneptune_sc_scene_volatility_short_term'] < volatility_median_short_term]

# 检查缺失值和无穷值
nan_df = factor_df_all.isnull().sum()
inf_df = factor_df_all.abs().max()>1e100
print('nan', nan_df[nan_df>0])
print('inf', inf_df[inf_df>0])
assert len(nan_df[nan_df>0])==0
assert len(inf_df[inf_df>0])==0

#检查情绪因子
# emotion_list=factor_bank_inf[factor_bank_inf['emotion']==1]['factor_name'].values
# for factor_name in factor_df_all.columns:
#     day_value_counts=factor_df_all[factor_name].groupby('dt').value_counts(normalize=True)
#     day_max_ratio=day_value_counts.groupby('dt').max()
#     if len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio)>0.9 and factor_name not in emotion_list:
#         print('less:',factor_name,len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio))
#     if len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio)<0.9 and factor_name in emotion_list:
#         print('more:',factor_name,len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio))

#检查因子列表
print(factor_df_all.shape,len(factor_bank_inf))
print([col for col in factor_df_all.columns if col not in factor_bank_inf['factor_name'].values])
print([col for col in factor_bank_inf['factor_name'].values if col not in factor_df_all.columns])
# assert len([col for col in factor_df_all.columns if col not in factor_bank_inf_all['factor_name'].values])==0
assert len([col for col in factor_bank_inf['factor_name'].values if col not in factor_df_all.columns])==0

# factor_df_all_long_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_filter_long_term_20170110_{test_end_date}.pkl')
factor_df_all_mid_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_filter_mid_term_20170110_{test_end_date}.pkl')
# factor_df_all_short_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_filter_short_term_20170110_{test_end_date}.pkl')
#
# factor_df_swing_high_long_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_sw_high_filter_long_term_20170110_{test_end_date}.pkl')
# factor_df_swing_low_long_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_sw_low_filter_long_term_20170110_{test_end_date}.pkl')
factor_df_swing_high_mid_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_sw_high_filter_mid_term_20170110_{test_end_date}.pkl')
factor_df_swing_low_mid_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_sw_low_filter_mid_term_20170110_{test_end_date}.pkl')
# factor_df_swing_high_short_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_sw_high_filter_short_term_20170110_{test_end_date}.pkl')
# factor_df_swing_low_short_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_sw_low_filter_short_term_20170110_{test_end_date}.pkl')
#
# factor_df_volatility_high_long_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_vol_high_filter_long_term_20170110_{test_end_date}.pkl')
# factor_df_volatility_low_long_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_vol_low_filter_long_term_20170110_{test_end_date}.pkl')
factor_df_volatility_high_mid_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_vol_high_filter_mid_term_20170110_{test_end_date}.pkl')
factor_df_volatility_low_mid_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_vol_low_filter_mid_term_20170110_{test_end_date}.pkl')
# factor_df_volatility_high_short_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_vol_high_filter_short_term_20170110_{test_end_date}.pkl')
# factor_df_volatility_low_short_term.loc[:pd.Timestamp(str(test_end_date))].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/{start_date}_{test_end_date}/factor_df_sc_vol_low_filter_short_term_20170110_{test_end_date}.pkl')

# 分享fit
# factor_df_all_long_term['scene_sw'] = 0
# factor_df_all_long_term.loc[factor_df_all_long_term['tsq_newneptune_sc_scene_swing_long_term'] >= swing_median_long_term,'scene_sw'] = 1
# factor_df_all_long_term['scene_vol'] = 0
# factor_df_all_long_term.loc[factor_df_all_long_term['tsq_newneptune_sc_scene_volatility_long_term'] >= volatility_median_long_term,'scene_vol'] = 1
# factor_df_all_long_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_filter_long_term_{start_date}_{end_date}.pkl')
# factor_df_swing_high_long_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_sw_high_filter_long_term_{start_date}_{end_date}.pkl')
# factor_df_swing_low_long_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_sw_low_filter_long_term_{start_date}_{end_date}.pkl')
# factor_df_volatility_high_long_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_vol_high_filter_long_term_{start_date}_{end_date}.pkl')
# factor_df_volatility_low_long_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_vol_low_filter_long_term_{start_date}_{end_date}.pkl')
#
# factor_df_all_mid_term['scene_sw'] = 0
# factor_df_all_mid_term.loc[factor_df_all_mid_term['tsq_newneptune_sc_scene_swing_mid_term'] >= swing_median_mid_term,'scene_sw'] = 1
# factor_df_all_mid_term['scene_vol'] = 0
# factor_df_all_mid_term.loc[factor_df_all_mid_term['tsq_newneptune_sc_scene_volatility_mid_term'] >= volatility_median_mid_term,'scene_vol'] = 1
# factor_df_all_mid_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_filter_mid_term_{start_date}_{end_date}.pkl')
# factor_df_swing_high_mid_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_sw_high_filter_mid_term_{start_date}_{end_date}.pkl')
# factor_df_swing_low_mid_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_sw_low_filter_mid_term_{start_date}_{end_date}.pkl')
# factor_df_volatility_high_mid_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_vol_high_filter_mid_term_{start_date}_{end_date}.pkl')
# factor_df_volatility_low_mid_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_vol_low_filter_mid_term_{start_date}_{end_date}.pkl')
#
# factor_df_all_short_term['scene_sw'] = 0
# factor_df_all_short_term.loc[factor_df_all_short_term['tsq_newneptune_sc_scene_swing_short_term'] >= swing_median_short_term,'scene_sw'] = 1
# factor_df_all_short_term['scene_vol'] = 0
# factor_df_all_short_term.loc[factor_df_all_short_term['tsq_newneptune_sc_scene_volatility_short_term'] >= volatility_median_short_term,'scene_vol'] = 1
# factor_df_all_short_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_filter_short_term_{start_date}_{end_date}.pkl')
# factor_df_swing_high_short_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_sw_high_filter_short_term_{start_date}_{end_date}.pkl')
# factor_df_swing_low_short_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_sw_low_filter_short_term_{start_date}_{end_date}.pkl')
# factor_df_volatility_high_short_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_vol_high_filter_short_term_{start_date}_{end_date}.pkl')
# factor_df_volatility_low_short_term.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/{start_date}_{end_date}/factor_df_sc_vol_low_filter_short_term_{start_date}_{end_date}.pkl')