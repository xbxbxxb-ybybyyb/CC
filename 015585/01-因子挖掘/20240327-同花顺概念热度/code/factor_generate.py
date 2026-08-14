import pandas as pd
import numpy as np
import itertools
import datetime
import IO
def rank_(data_):
    data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
    return data_r
def f_calc_max(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.max()
def f_calc_mean(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.mean()
func_dic = {'max':f_calc_max,
            'mean':f_calc_mean}
m_list = [1,5,10]
df = pd.read_pickle('/dfs/user/015585/20240327-同花顺概念热度/file/res_theme_stock_heat.pkl')
df = df.set_index(['dt','Ticker'])

for func,m in itertools.product(func_dic,m_list):
    for is_rank in ['value','rank']:
        factor_name = 'factor_{}_{}_{}'.format(func,m,is_rank)
        print(factor_name)
        if func == 'max':
            factor_df = pd.DataFrame(df.groupby(['dt','Ticker'])['val1'].max())
        elif func == 'mean':
            factor_df = pd.DataFrame(df.groupby(['dt', 'Ticker'])['val1'].mean())
        else:
            raise TypeError('输入了错误的函数')
        factor_df.columns = [factor_name]
        if m > 1:
            factor_df[factor_name] = factor_df[factor_name].unstack().rolling(m,1).mean().stack()
        if is_rank == 'rank':
            factor_df[factor_name] = rank_(factor_df[factor_name])
        path = '/dfs/user/015585/20240327-同花顺概念热度/factor/' + factor_name + '.h5'
        with pd.HDFStore(path) as h5_store:
            h5_store.put('data', factor_df, format='table', append=False, data_columns=True)
            h5_store.get_storer('data').attrs.modification_date = datetime.datetime.today()
