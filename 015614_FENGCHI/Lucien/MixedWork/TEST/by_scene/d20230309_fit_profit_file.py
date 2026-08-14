# coding: utf-8
# Author：fengchi863
# Date ：2023/3/9 14:17

"""
使用市场高度作为配置文件
方式一：修改信号文件，低于几板的天数不买；
方式二：修改收益文件，低于几板的天数，收益文件买入金额为0或者减半，或者增加；
"""

import pandas as pd
import numpy as np
from LucienUtil.FileUtil import FileUtil

def trans_signal(signal_fpath, tag='method1'):
    signal = pd.read_csv(signal_fpath, index_col=0)
    signal['buy_amt_coef'] = signal['datelist'].apply(lambda x: mh.loc[x, 'buy_amt_coef']).astype(bool)
    signal['prediction'] = signal['prediction'] * signal['buy_amt_coef']
    signal = signal.drop(['buy_amt_coef'], axis=1)

    new_fpath = signal_fpath[:-4] + f'_{tag}' + signal_fpath[-4:]
    signal.to_csv(new_fpath)

mh = pd.read_pickle('/data/user/015614/TEST/分场景/lb_hegiht_20160101_20221231.pkl')
mh = pd.DataFrame(mh)
"""
# 方案一
mh['buy_amt_coef'] = np.nan
mh.loc[mh[0] <= 2, 'buy_amt_coef'] = 0
mh.loc[(mh[0] > 2) & (mh[0] < 7), 'buy_amt_coef'] = 1
mh.loc[(mh[0] >= 7), 'buy_amt_coef'] = 1
mh = mh.shift(1)

# 测试信号，使用Europa v2_0_4 V3模型的信号进行交易
origin_signal_v1_test_fpath = '/data/user/015614/Zeus/pred/Europa/v2_0_4/LgbRegModelV3/20191001~20200331_LgbRegModelV3_v1.csv'
origin_signal_v1_fit_fpath = '/data/user/015614/Zeus/pred/Europa/v2_0_4/LgbRegModelV3/20200401~20201231_LgbRegModelV3_v1.csv'

trans_signal(origin_signal_v1_test_fpath, tag='method1')
trans_signal(origin_signal_v1_fit_fpath, tag='method1')
"""

# 方案二
mh['buy_amt_coef'] = np.nan
mh.loc[mh[0] <= 2, 'buy_amt_coef'] = 0
mh.loc[(mh[0] > 2) & (mh[0] < 6), 'buy_amt_coef'] = 1
mh.loc[(mh[0] >= 6), 'buy_amt_coef'] = 1.3
mh = mh.shift(1)

profit_fpath = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5'
profit_df = pd.read_hdf(profit_fpath)
profit_df['datelist'] = profit_df.index.get_level_values(0).strftime('%Y%m%d').astype(int)
profit_df['buy_amt_coef'] = profit_df['datelist'].apply(lambda x: mh.loc[x, 'buy_amt_coef'] if x in mh.index else 0)
profit_df['buy_amt'] = profit_df['buy_amt'] * profit_df['buy_amt_coef']
profit_df.to_hdf('/data/user/015614/Zeus/pred/Europa/v2_0_4/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30_v2.h5', key='profit')

# 统计工作
profit_df['mh'] = profit_df['datelist'].apply(lambda x: mh.loc[x, 0] if x in mh.index else 0)
profit_df = profit_df.query(f'datelist > 20160101 & datelist < 20221231')
all_group_pct = profit_df.groupby('mh')['pct'].agg(['mean', 'count'])
profit_df['year'] = profit_df['datelist'] // 10000
yearly_group_pct = profit_df.groupby(['year', 'mh'])['pct'].agg(['mean', 'count'])
res_dict = {'分组': all_group_pct,
            '按年分组': yearly_group_pct}
FileUtil.save_dict2xls(res_dict, '/data/user/015614/junkData/', '20230313_V2.xlsx')
from dataApi.sendInfo import send_file
send_file('/data/user/015614/junkData/20230313_V2.xlsx')
