import pandas as pd
import decimal
from tqdm import tqdm

def round_(x, n=13):
    x = x + 1e-15
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

strategy_version = 20250603
start_date, end_date = 20170110, 20220630

factor_bank_inf = pd.read_excel(f'/data/group/800463/tangsq/neptune/{strategy_version}/factor_bank_inf_sc.xlsx')

# 区间3 fit
factor_df_sc = pd.read_pickle(f'/dfs/user/023859/neptune/{strategy_version}/factor_df_sc_{start_date}_{end_date}.pkl')
# factor_df_2_ = pd.read_pickle(f'/dfs/user/023859/neptune/{strategy_version}/factor_df_20220101_20220630.pkl')
# assert len(set(factor_df_2_.columns)-set(factor_df_1.columns)) == 0
# assert len(factor_df_1.drop(columns=['buy_amt','label_t2o10dc_neg','label_t2o10dc_pos']).columns) == len(factor_df_2_.columns)

# profit_df = pd.read_hdf(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/zz1000_profit_interval.h5').loc[pd.Timestamp(str(start_date_append)):pd.Timestamp(str(end_date_append))]
label_df = pd.read_pickle(f'/dfs/user/023859/neptune/{strategy_version}/label_df_sc_20170110_20241231.pkl').loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
# label_df = pd.read_pickle(f'/dfs/user/023859/neptune/20250513/label_df_T0_20170110_20250331.pkl').loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
factor_df_all = label_df[['buy_amt','weight','label_t2o10dc_neg','label_t2o10dc_pos']].join(factor_df_sc)
assert len(factor_df_all) == len(label_df)

# filter: 剔除权重小于万5的样本,波动率小于千3的样本
factor_df_all = factor_df_all[factor_df_all['tsq_newneptune_sc_scene_volatility'] >= 0.003]
factor_df_all = factor_df_all[factor_df_all['weight'] >= 0.0005]

# 分场景
# swing_median = factor_df_all.loc[:pd.Timestamp('20200630')]['tsq_newneptune_s1_scene_swing'].median()
# factor_df_swing_high = factor_df_all[factor_df_all['tsq_newneptune_s1_scene_swing'] >= swing_median]
# factor_df_swing_low = factor_df_all[factor_df_all['tsq_newneptune_s1_scene_swing'] < swing_median]

volatility_median = factor_df_all.loc[:pd.Timestamp('20201231')]['tsq_newneptune_sc_scene_volatility'].median()
factor_df_volatility_high = factor_df_all[factor_df_all['tsq_newneptune_sc_scene_volatility'] >= volatility_median]
factor_df_volatility_low = factor_df_all[factor_df_all['tsq_newneptune_sc_scene_volatility'] < volatility_median]

# 保留13位有效数字
mm=factor_df_all.abs().max()
print(mm[mm>1e15])
for col in tqdm(factor_bank_inf['factor_name'].to_list()):
    # if col not in ['zwh_20240201_001','qyh_neptune_20250327_31']:
    factor_df_all[col]=factor_df_all[col].round(13)

assert len(factor_df_all) == len(factor_df_all.dropna())

# 检查缺失值和无穷值
nan_df = factor_df_all.isnull().sum()
inf_df = factor_df_all.abs().max()>1e100
print('nan', nan_df[nan_df>0])
print('inf', inf_df[inf_df>0])
assert len(nan_df[nan_df>0])==0
assert len(inf_df[inf_df>0])==0

#检查情绪因子
emotion_list=factor_bank_inf[factor_bank_inf['emotion']==1]['factor_name'].values
for factor_name in factor_df_all.columns:
    day_value_counts=factor_df_all[factor_name].groupby('dt').value_counts(normalize=True)
    day_max_ratio=day_value_counts.groupby('dt').max()
    if len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio)>0.9 and factor_name not in emotion_list:
        print('less:',factor_name,len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio))
    if len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio)<0.9 and factor_name in emotion_list:
        print('more:',factor_name,len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio))

#检查因子列表
print(factor_df_all.shape,len(factor_bank_inf))
print([col for col in factor_df_all.columns if col not in factor_bank_inf['factor_name'].values])
print([col for col in factor_bank_inf['factor_name'].values if col not in factor_df_all.columns])
# assert len([col for col in factor_df_all.columns if col not in factor_bank_inf_all['factor_name'].values])==0
assert len([col for col in factor_bank_inf['factor_name'].values if col not in factor_df_all.columns])==0

factor_df_all.loc[:pd.Timestamp('20210630')].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/factor_df_sc_filter_20170110_20210630.pkl')
# factor_df_swing_high.loc[:pd.Timestamp('20201231')].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/factor_df_s1_sw_high_filter_20170110_20201231.pkl')
# factor_df_swing_low.loc[:pd.Timestamp('20201231')].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/factor_df_s1_sw_low_filter_20170110_20201231.pkl')
factor_df_volatility_high.loc[:pd.Timestamp('20210630')].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/factor_df_sc_vol_high_filter_20170110_20210630.pkl')
factor_df_volatility_low.loc[:pd.Timestamp('20210630')].to_pickle(f'/data/group/800463/tangsq/neptune/{strategy_version}/factor_df_sc_vol_low_filter_20170110_20210630.pkl')

# factor_df_all['scene_sw'] = 0
# factor_df_all.loc[factor_df_all['tsq_newneptune_s1_scene_swing'] >= swing_median,'scene_sw'] = 1
factor_df_all['scene_vol'] = 0
factor_df_all.loc[factor_df_all['tsq_newneptune_sc_scene_volatility'] >= volatility_median,'scene_vol'] = 1

factor_df_all.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/factor_df_sc_filter_{start_date}_{end_date}.pkl')
factor_df_all.to_pickle(f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/factor_df_sc_filter_{start_date}_{end_date}.pkl')
# factor_df_swing_high.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/factor_df_s1_sw_high_filter_{start_date}_{end_date}.pkl')
# factor_df_swing_high.to_pickle(f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/factor_df_s1_sw_high_filter_{start_date}_{end_date}.pkl')
# factor_df_swing_low.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/factor_df_s1_sw_low_filter_{start_date}_{end_date}.pkl')
# factor_df_swing_low.to_pickle(f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/factor_df_s1_sw_low_filter_{start_date}_{end_date}.pkl')
factor_df_volatility_high.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/factor_df_sc_vol_high_filter_{start_date}_{end_date}.pkl')
factor_df_volatility_high.to_pickle(f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/factor_df_sc_vol_high_filter_{start_date}_{end_date}.pkl')
factor_df_volatility_low.to_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/factor_df_sc_vol_low_filter_{start_date}_{end_date}.pkl')
factor_df_volatility_low.to_pickle(f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/factor_df_sc_vol_low_filter_{start_date}_{end_date}.pkl')