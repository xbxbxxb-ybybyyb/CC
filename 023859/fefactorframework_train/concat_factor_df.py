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

# factor_bank_inf_all = pd.read_excel('/data/group/800463/tangsq/neptune/20250506/factor_bank_inf.xlsx')
# factor_df_all_old = pd.read_pickle('/data/group/800463/tangsq/neptune/20250506/factor_df_20170110_20191231.pkl')
factor_bank_inf = pd.read_excel('/dfs/user/023859/neptune/20250513/factor_bank_inf.xlsx')

factor_df = pd.read_pickle('/dfs/user/023859/neptune/20250513/factor_df_20170110_20200630.pkl')
label_df = pd.read_pickle('/dfs/user/023859/neptune/20250513/label_df_detail_20160101_20250331.pkl')
factor_df_all['buy_amt'] = label_df['buy_amt']
factor_df_all['buy_amt'] = label_df['buy_amt']

factor_df_all = label_df[['buy_amt','']]
factor_df_all = factor_df_all.dropna()
factor_df_all.insert(0,'buy_amt',factor_df_all.pop('buy_amt'))

# 保留13位有效数字
mm=factor_df_all.abs().max()
print(mm[mm>1e15])
for col in tqdm(factor_bank_inf_all['factor_name'].to_list()):
    if col not in ['zwh_20240201_001','qyh_neptune_20250327_31']:
        factor_df_all[col]=factor_df_all[col].apply(round_)

# 检查缺失值和无穷值
nan_df = factor_df_all.isnull().sum()
inf_df = factor_df_all.abs().max()>1e100
print('nan', nan_df[nan_df>0])
print('inf', inf_df[inf_df>0])
assert len(nan_df[nan_df>0])==0
assert len(inf_df[inf_df>0])==0

#检查情绪因子
emotion_list=factor_bank_inf_all[factor_bank_inf_all['emotion']==1]['factor_name'].values
for factor_name in factor_df_all.columns:
    day_value_counts=factor_df_all[factor_name].groupby('dt').value_counts(normalize=True)
    day_max_ratio=day_value_counts.groupby('dt').max()
    if len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio)>0.9 and factor_name not in emotion_list:
        print('less:',factor_name,len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio))
    if len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio)<0.9 and factor_name in emotion_list:
        print('more:',factor_name,len(day_max_ratio[day_max_ratio>0.9])/len(day_max_ratio))

#检查因子列表
print(factor_df_all.shape,len(factor_bank_inf_all))
print([col for col in factor_df_all.columns if col not in factor_bank_inf_all['factor_name'].values])
print([col for col in factor_bank_inf_all['factor_name'].values if col not in factor_df_all.columns])
# assert len([col for col in factor_df_all.columns if col not in factor_bank_inf_all['factor_name'].values])==0
assert len([col for col in factor_bank_inf_all['factor_name'].values if col not in factor_df_all.columns])==0

factor_df_all['label_t2o10dc'] = -factor_df_all['label_t2o10dc']
print(factor_df_all_old.shape, factor_df_all.shape)
assert factor_df_all_old.shape[1] == factor_df_all.shape[1]
factor_df_all = pd.concat([factor_df_all_old,factor_df_all])
factor_df_all.to_pickle('/dfs/user/023859/share_file/for_wj/neptune/20250506/factor_df_20170110_20201231.pkl')