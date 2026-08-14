import pandas as pd
import os
from tqdm import tqdm
from multiprocessing import Pool

def calc_corr(df, factor):
    sta_df = pd.DataFrame(index=label_list)
    for label in label_list:
        sta_df.loc[label, f'{factor}'] = df.groupby('dt').apply(lambda x: x[f'{factor}'].rank().corr(x[label].rank())).mean()  # 截面IC
    return sta_df

start_date, end_date = 20200101, 20231231 # 数据起始日期
strategy_path = '/dfs/user/023859/share_file/for_qyh/neptune/飞笛舆情测试' # 策略数据存储路径
factor_bank_inf_path = '/dfs/group/800463/public/projectZZ_public/factor_lib/check_res_tot_neptune.xlsx'
label_short = pd.read_hdf('/data/user/023859/factor_zooZZ/factor_lib/sft_basic_formal_931_20160101_20241231.h5').loc[pd.Timestamp('20200101'):pd.Timestamp('20231231')]
label_long = pd.read_hdf('/data/user/023859/factor_zooZZmkt/factor_lib/sft_basic_formal_931_20160101_20241231.h5').loc[pd.Timestamp('20200101'):pd.Timestamp('20231231')]
label_df = pd.concat([label_short[['label_s1_short','label_s1_mid','label_s1_long']],label_long[['label_t2o30d1','label_t4o30d1','label_t6o30d1','label_t11o30d1']]],axis=1)
label_list = ['label_s1_short','label_s1_mid','label_s1_long','label_t2o30d1','label_t4o30d1','label_t6o30d1','label_t11o30d1']

all_factor_path_0 = f'/dfs/user/023859/neptune/20250720/20170110_20201231/factor_value/neptune' # 后续区间因子计算路径
all_factor_path_1 = f'/dfs/user/023859/neptune/20250720/20210101_20231231/factor_value/neptune' # 后续区间因子计算路径

# 可用因子列表
factors_check_res = pd.read_excel(factor_bank_inf_path)
factors_check_res = factors_check_res[factors_check_res['pre_check'] == 'pass']
factors_available = factors_check_res['factor_name'].to_list()
print(f'可用因子数：{len(factors_available)}个')

factor_list_0 = []
factor_list_1 = []

filenames = os.listdir(all_factor_path_0)
for file in tqdm(filenames):
    if file.split('.')[0] in factors_available:
        factor_path = os.path.join(all_factor_path_0,file)
        factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
        factor_list_0.append(factor)
factor_df0 = pd.concat(factor_list_0,axis=1)
#
filenames = os.listdir(all_factor_path_1)
for file in tqdm(filenames):
    if file.split('.')[0] in factors_available:
        factor_path = os.path.join(all_factor_path_1,file)
        factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
        factor_list_1.append(factor)
factor_df1 = pd.concat(factor_list_1,axis=1)

factor_df = pd.concat([factor_df0,factor_df1],axis=0)
factor_df.to_pickle('/dfs/user/023859/share_file/for_qyh/飞笛舆情测试/df_neptune_factors.pkl')
# basic_df = factor_df.join(label_df)
#
# with Pool(processes=24) as pool:
#     results = pool.starmap(calc_corr,[(basic_df[label_list+[factor]], factor) for factor in factor_df.columns])
#
# res = pd.concat(results,axis=1)
# res.T.to_pickle('/dfs/user/023859/share_file/for_qyh/飞笛舆情测试/neptune_IC.pkl')