import pandas as pd
import os
from tqdm import tqdm

factor_version_date = 20250729 # 策略迭代版本
start_date, end_date = 20210101, 20231231 # 数据起始日期
strategy_path = os.path.join('/dfs/user/023859/share_file/for_qyh/neptune',str(factor_version_date)) # 策略数据存储路径
basic_file_path = f'/dfs/user/023859/neptune/20250609/basic_file_zz1000_s1_20170110_20241231.pkl' # 基础样本文件路径
factor_bank_inf_path = os.path.join(strategy_path,'factor_bank_inf_s7.xlsx') # 可用因子列表
all_factor_path_in_sample = '/data/user/023859/factor_zooZZ/all_factor/931' # 因子库路径
all_factor_path_out_sample_1 = f'/dfs/user/023859/neptune/20250526/20210101_20211231/factor_value/neptune' # 后续区间因子计算路径
# all_factor_path_out_sample_2 = f'/dfs/user/023859/neptune/20250526/20220101_20221231/factor_value/neptune' # 后续区间因子计算路径
# all_factor_path_out_sample_3 = f'/dfs/user/023859/neptune/20250526/20230101_20231231/factor_value/neptune' # 后续区间因子计算路径

t_factor_path_dict = {
    # 't_factor_path_1':'/dfs/user/018107/share_file/for_tsq/20250729_zz1000_931_t_factor_20170101_20211231.pkl',
    # 't_factor_path_2':'/dfs/user/018107/share_file/for_tsq/20250729_zz1000_1301_t_factor_20170101_20211231.pkl',
    # 't_factor_path_3':'/dfs/user/018107/share_file/for_tsq/20250729_zz1000_1445_t_factor_20170101_20211231.pkl',
    't_factor_path_4':'/dfs/user/018107/share_file/for_tsq/20250729_zz1000_ammax_t_factor_20170101_20211231.pkl',
    't_factor_path_5':'/dfs/user/018107/share_file/for_tsq/20250729_zz1000_max_t_factor_20170101_20211231.pkl',
    't_factor_path_6':'/dfs/user/018107/share_file/for_tsq/20250729_zz1000_min_t_factor_20170101_20211231.pkl',
    't_factor_path_7':'/dfs/user/018107/share_file/for_tsq/20250729_zz1000_pmmax_t_factor_20170101_20211231.pkl'
}

# emotion_factor_path = f'/dfs/user/023859/neptune/20250527/index_emotion_factors/20160101_20250331' # 情绪因子路径
# scene_swing_factor_path = f'/dfs/user/023859/neptune/{factor_version_date}/scene_factors_swing/20170110_20241231' # 分场景因子路径
# scene_volatility_factor_path = f'/dfs/user/023859/neptune/{factor_version_date}/scene_factors_volatility/20170110_20241231' # 分场景因子路径

# 读取basic
basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

# 可用因子列表
factors_check_res = pd.read_excel(factor_bank_inf_path)
factors_available = factors_check_res['factor_name'].to_list()
print(f'可用因子数：{len(factors_available)}个')

factor_df_all = pd.read_pickle('/dfs/user/023859/neptune/20250609/factor_df_s1_20170110_20220630.pkl')
factor_df = factor_df_all[factors_check_res[factors_check_res['t']=='T-1']['factor_name'].tolist()]

# factor_list_in_sample = []
# factor_list_out_sample_1 = []
# # factor_list_out_sample_2 = []
# # factor_list_out_sample_3 = []
#
# filenames_in_sample = os.listdir(all_factor_path_in_sample)
# for file in tqdm(filenames_in_sample):
#     if file in factors_available:
#         factor_path = os.path.join(all_factor_path_in_sample,file,file+'.h5')
#         factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
#         factor_list_in_sample.append(factor)
#
# factor_df_in_sample = pd.concat(factor_list_in_sample,axis=1)
#
# filenames_out_sample_1 = os.listdir(all_factor_path_out_sample_1)
# for file in tqdm(filenames_out_sample_1):
#     if file.split('.')[0] in factors_available:
#         factor_path = os.path.join(all_factor_path_out_sample_1,file)
#         factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
#         factor_list_out_sample_1.append(factor)
# factor_df_out_sample_1 = pd.concat(factor_list_out_sample_1,axis=1)

# filenames_out_sample_2 = os.listdir(all_factor_path_out_sample_2)
# for file in tqdm(filenames_out_sample_2):
#     if file.split('.')[0] in factors_available:
#         factor_path = os.path.join(all_factor_path_out_sample_2,file)
#         factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
#         factor_list_out_sample_2.append(factor)
# factor_df_out_sample_2 = pd.concat(factor_list_out_sample_2,axis=1)
#
# filenames_out_sample_3 = os.listdir(all_factor_path_out_sample_3)
# for file in tqdm(filenames_out_sample_3):
#     if file.split('.')[0] in factors_available:
#         factor_path = os.path.join(all_factor_path_out_sample_3,file)
#         factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
#         factor_list_out_sample_3.append(factor)
# factor_df_out_sample_3 = pd.concat(factor_list_out_sample_3,axis=1)

# factor_df = pd.concat([factor_df_in_sample,factor_df_out_sample_1],axis=0).sort_index()

# 读取情绪因子
# emotion_filenames = os.listdir(emotion_factor_path)
# for file in tqdm(emotion_filenames):
#     factor_path = os.path.join(emotion_factor_path,file)
#     factor = pd.read_hdf(factor_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
#     factor_list.append(factor)

# 读取分场景因子
# factor_list.append(pd.read_hdf(os.path.join(scene_volatility_factor_path,'tsq_newneptune_s1_index_scene_volatility.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])
# factor_list.append(pd.read_hdf(os.path.join(scene_volatility_factor_path,'tsq_newneptune_s1_scene_volatility_long_term.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])
# factor_list.append(pd.read_hdf(os.path.join(scene_volatility_factor_path,'tsq_newneptune_s1_scene_volatility_mid_term.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])
# factor_list.append(pd.read_hdf(os.path.join(scene_volatility_factor_path,'tsq_newneptune_s1_scene_volatility_short_term.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])
#
# factor_list.append(pd.read_hdf(os.path.join(scene_swing_factor_path,'tsq_newneptune_s1_scene_swing_long_term.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])
# factor_list.append(pd.read_hdf(os.path.join(scene_swing_factor_path,'tsq_newneptune_s1_scene_swing_mid_term.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])
# factor_list.append(pd.read_hdf(os.path.join(scene_swing_factor_path,'tsq_newneptune_s1_scene_swing_short_term.h5')).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))])

# 少森那边的t日因子
for t_factor_path in t_factor_path_dict.keys():
    t = t_factor_path_dict[t_factor_path].split('/')[-1].split('_')[2]
    factor_df_t = pd.read_pickle(t_factor_path_dict[t_factor_path])
    factor_df_t = factor_df_t.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]

    all_factors = pd.concat([factor_df_t, factor_df],axis=1)
    assert len(set(factors_available)-set(all_factors.columns))==0

    all_factor_df = basic_file.join(all_factors)
    # assert len(all_factor_df) == len(all_factor_df.dropna())
    # 原始因子值
    all_factor_df.to_pickle(os.path.join(strategy_path, f'factor_df_{t}_{start_date}_{end_date}.pkl'))
