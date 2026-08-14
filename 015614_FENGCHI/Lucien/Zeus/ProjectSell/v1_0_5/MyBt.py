# coding: utf-8
# Author：fengchi863
# Date ：2023/4/4 10:30

import pandas as pd

period4_test_fpath_list = [
    '/data/user/015614/Zeus/pred/ProjectSell/v1_0_5/LgbRegModelV2/20210701~20211231_LgbRegModelV2_v4.csv',
    '/data/user/015614/Zeus/pred/ProjectSell/v1_0_5/LgbRegModelV3/20210701~20211231_LgbRegModelV2_v4.csv',
    '/data/user/015614/Zeus/pred/ProjectSell/v1_0_5/XgbRegModelV2/20210701~20211231_LgbRegModelV2_v4.csv',
    '/data/user/015614/Zeus/pred/ProjectSell/v1_0_5/XgbRegModelV3/20210701~20211231_LgbRegModelV2_v4.csv',
]

for test_fpath in period4_test_fpath_list:
    samples = pd.read_csv(test_fpath, index_col=0)
    samples['dt'] = samples['datelist'].apply(lambda x: pd.to_datetime(str(x)))

    # profit与所有Europa买入样本合并
    profit = pd.read_hdf('/data/group/800463/sunss/project_sell/newData/Sell_pct_0.10_800_190_SH450_SZ100.h5')
    europa_samples = pd.read_pickle('/data/group/800463/sunss/europa/20230317/factor_df_all_20160101_20211231.pkl')
    profit['sell_date'] = profit.index.get_level_values(0)
    profit['Ticker'] = profit.index.get_level_values(1)
    profit['dt'] = profit['dt_last_zt_1_ts']
    profit['buy_datelist'] = profit['dt_last_zt_1_ts'].apply(lambda x: int(x.strftime('%Y%m%d')))
    profit = profit.query(f'buy_datelist >= 20210701 & buy_datelist <= 20211231')
    profit = profit.set_index(['dt', 'Ticker'])
    profit = profit.loc[list(set(europa_samples.index).intersection(set(profit.index)))].sort_index()

    # 合并信号
    samples['dt'] = samples['datelist'].apply(lambda x: pd.to_datetime(str(x)))
    samples['Ticker'] = samples['stockID']
    samples = samples.set_index(['dt', 'Ticker'])
    profit['dt'] = profit['sell_date']
    profit['Ticker'] = profit.index.get_level_values(1)
    profit = profit.set_index(['dt', 'Ticker'])
    combine = pd.merge(profit, samples, on=['dt', 'Ticker'])

