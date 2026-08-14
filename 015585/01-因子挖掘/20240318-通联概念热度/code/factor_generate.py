import pandas as pd
import numpy as np
import itertools
import datetime
import IO
'''
1、n=1,3，前n名的主题热度均值作为个股当日热度，m = 1,5,10，前m天的个股当日热度均值作为最终因子值（T-1_Factor）
'''
n_list = [1,2,3]
m_list = [1,5,10]
df = pd.read_pickle('/dfs/user/015585/20240318-通联概念热度/file_res/res.pkl')
df = df.reset_index()
df = df[df['insertTime'] < df['dt'] + datetime.timedelta(days=1)] # 剔除主题未insert但是已有主题热度的情况，也剔除空值情况
# 筛选交易日部分
md_data = IO.read_data([20190315, 20240315],
                          columns=['amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
df = df.set_index(['dt','Ticker'])
def rank_(data_):
    data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
    return data_r
for n,m in itertools.product(n_list,m_list):
    for is_rank in ['value','rank']:
        factor_name = 'factor_{}_{}_{}'.format(n,m,is_rank)
        print(factor_name)
        factor_df = pd.DataFrame(df[df['corr_rank'] <= n].groupby(['dt','Ticker'])['heat'].mean())
        factor_df.columns = [factor_name]
        factor_df = factor_df.reindex((factor_df.index) & (md_data.index))
        if m > 1:
            factor_df[factor_name] = factor_df[factor_name].unstack().rolling(m,1).mean().stack()
        if is_rank == 'rank':
            factor_df[factor_name] = rank_(factor_df[factor_name])
        path = '/dfs/user/015585/20240318-通联概念热度/factor/' + factor_name + '.h5'
        with pd.HDFStore(path) as h5_store:
            h5_store.put('data', factor_df, format='table', append=False, data_columns=True)
            h5_store.get_storer('data').attrs.modification_date = datetime.datetime.today()
