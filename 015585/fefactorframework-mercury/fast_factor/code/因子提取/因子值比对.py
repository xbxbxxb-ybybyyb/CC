import pandas as pd

df1 = pd.read_hdf('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250820_xdbtick1m/factor_value/neptune/930_after_all_all_0_bigger_all_b2transtd_med.h5')
df2 = pd.read_hdf('/data/user/015585/20240116_frame/factor_value/neptune/qyh_neptune_shortterm_20250821_1.h5')

sft_basic_path = '/dfs/user/015585/test/zz1000/sft_zz1000_2017_2021.pkl'
df = pd.read_pickle(sft_basic_path)


