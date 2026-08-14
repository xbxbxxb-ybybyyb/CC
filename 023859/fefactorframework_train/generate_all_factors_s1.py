import pandas as pd
import os
from tqdm import tqdm

factor_version_date = 20250609 # 策略迭代版本
start_date, end_date = 20170110, 20220630 # 数据起始日期
strategy_path = os.path.join('/dfs/user/023859/neptune',str(factor_version_date)) # 策略数据存储路径
basic_file_path = f'/dfs/user/023859/neptune/{factor_version_date}/basic_file_zz1000_s1_20170110_20241231.pkl' # 基础样本文件路径
factor_bank_inf_path = os.path.join(strategy_path,'factor_bank_inf_s1.xlsx') # 可用因子列表
all_factor_path_in_sample = '/data/user/023859/factor_zooZZ/all_factor/931' # 因子库路径
all_factor_path_out_sample_1 = f'/dfs/user/023859/neptune/20250526/20210101_20211231/factor_value/neptune' # 后续区间因子计算路径
all_factor_path_out_sample_2 = f'/dfs/user/023859/neptune/20250526/20220101_20221231/factor_value/neptune' # 后续区间因子计算路径
t_factor_path = '/dfs/user/018107/share_file/for_tsq/20250522_zz1000_factor_value_20160101_20220630.pkl'
emotion_factor_path = f'/dfs/user/023859/neptune/20250527/index_emotion_factors/20160101_20250331' # 情绪因子路径
# scene_swing_factor_path = f'/dfs/user/023859/neptune/20250527/scene_factors_swing/20170110_20241231' # 分场景因子路径
scene_volatility_factor_path = f'/dfs/user/023859/neptune/{factor_version_date}/scene_factors_volatility/20170110_20241231' # 分场景因子路径

# 读取basic
basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

# 可用因子列表
factors_check_res = pd.read_excel(factor_bank_inf_path)
factors_available = factors_check_res['factor_name'].to_list()
print(f'可用因子数：{len(factors_available)}个')

factor_list = []
factor_list_in_sample = []
factor_list_out_sample_1 = []
factor_list_out_sample_2 = []

filenames_in_sample = os.listdir(all_factor_path_in_sample)
for file in tqdm(filenames_in_sample):
    if file in factors_available:
        factor_path = os.path.join(all_factor_path_in_sample,file,file+'.h5')
        factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
        factor_list_in_sample.append(factor)

factor_df_in_sample = pd.concat(factor_list_in_sample,axis=1)

filenames_out_sample_1 = os.listdir(all_factor_path_out_sample_1)
for file in tqdm(filenames_out_sample_1):
    if file.split('.')[0] in factors_available:
        factor_path = os.path.join(all_factor_path_out_sample_1,file)
        factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
        factor_list_out_sample_1.append(factor)
factor_df_out_sample_1 = pd.concat(factor_list_out_sample_1,axis=1)

filenames_out_sample_2 = os.listdir(all_factor_path_out_sample_2)
for file in tqdm(filenames_out_sample_2):
    if file.split('.')[0] in factors_available:
        factor_path = os.path.join(all_factor_path_out_sample_2,file)
        factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
        factor_list_out_sample_2.append(factor)
factor_df_out_sample_2 = pd.concat(factor_list_out_sample_2,axis=1)

factor_df = pd.concat([factor_df_in_sample,factor_df_out_sample_1,factor_df_out_sample_2],axis=0).sort_index()

# 读取情绪因子
emotion_filenames = os.listdir(emotion_factor_path)
for file in tqdm(emotion_filenames):
    factor_path = os.path.join(emotion_factor_path,file)
    factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    factor_list.append(factor)

# 读取分场景因子
# factor_list.append(pd.read_hdf(os.path.join(scene_volatility_factor_path,'tsq_newneptune_s1_index_scene_volatility.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])
factor_list.append(pd.read_hdf(os.path.join(scene_volatility_factor_path,'tsq_newneptune_s1_scene_volatility_long_term.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])
factor_list.append(pd.read_hdf(os.path.join(scene_volatility_factor_path,'tsq_newneptune_s1_scene_volatility_mid_term.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])
factor_list.append(pd.read_hdf(os.path.join(scene_volatility_factor_path,'tsq_newneptune_s1_scene_volatility_short_term.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])

# factor_list.append(pd.read_hdf(os.path.join(scene_swing_factor_path,'tsq_newneptune_s1_index_scene_swing.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])
# factor_list.append(pd.read_hdf(os.path.join(scene_swing_factor_path,'tsq_newneptune_s1_scene_swing.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])

# 少森那边的t日因子
factor_df_t = pd.read_pickle(t_factor_path)
factor_df_t = factor_df_t.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
factor_list.append(factor_df_t)

all_factors_other = pd.concat(factor_list,axis=1)
all_factors = pd.concat([all_factors_other, factor_df],axis=1)
assert len(all_factors.columns) == len(factors_available)

all_factor_df = basic_file.join(all_factors)
assert len(all_factor_df) == len(all_factor_df.dropna())
# 原始因子值
all_factor_df.to_pickle(os.path.join(strategy_path, f'factor_df_s1_{start_date}_{end_date}.pkl'))
