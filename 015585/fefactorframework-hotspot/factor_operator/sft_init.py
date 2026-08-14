import pandas as pd

'''
制作sft初始文件
2025-03-07：4个基础因子
'''
factor_list = [
    # 'factor_qyh_hotspot_pct5',
    # 'factor_qyh_hotspot_pct20high',
    # 'factor_qyh_hotspot_pre_close',
    # 'factor_qyh_hotspot_turn'
]
factor_list = [i.replace('factor_','') for i in factor_list]
df = pd.DataFrame()
for factor in factor_list:
    df[factor] = pd.read_hdf(f'/data/user/015585/factors_hotspot/factor_value/hotspot/{factor}.h5')[factor]

#
path_basic = '/dfs/user/020412/团队分享/for_hotspot/md2_20250611_20150901_20231231.h5'
path_type = 'pct35'
out_path_pkl = f'/dfs/user/015585/00_hotspot/basic_files/factor_files/{path_type}/md2_20250611_20150901_20231231.pkl'
out_path_h5 = f'/dfs/user/015585/00_hotspot/basic_files/factor_files/{path_type}/md2_20250611_20150901_20231231.h5'
# sft_init
basic_file = pd.read_hdf(path_basic)
basic_file = basic_file.sort_values(['dt','Ticker'])
# df = pd.merge(basic_file[['reward']],df,left_index=True,right_index=True,how = 'left')
df = basic_file[['reward']]
df = df.rename(columns = {'reward':'label'})
df.loc[pd.Timestamp('20160101'):pd.Timestamp('20231231')].to_pickle(f'/dfs/user/015585/00_hotspot/basic_files/factor_files/{path_type}/sft_init_20160101_20231231.pkl')
print('完成sft_init')

# 转存basic pkl格式
basic_file = pd.read_hdf(path_basic).sort_values(['dt','Ticker'])
basic_file.to_pickle(out_path_pkl)
print('完成basic pkl格式')

# 转存basic h5格式
basic_file = pd.read_hdf(path_basic).sort_values(['dt','Ticker'])
with pd.HDFStore(out_path_h5) as h5_store:
    h5_store.put('data', basic_file, format='table', append=False, data_columns=True)
    import datetime
    h5_store.get_storer('data').attrs.modification_date = datetime.datetime.today()
print('完成basic h5格式')