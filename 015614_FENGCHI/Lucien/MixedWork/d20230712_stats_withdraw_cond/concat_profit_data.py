# coding: utf-8
# Author：fengchi863
# Date ：2023/7/21 17:32

"""
没办法利用trans来进行研究：比如直接用trans判断是否要撤单，那就是要判断是否有这类时刻，但很可能策略在
"""

import pandas as pd

withdraw_path = '/arch1/user/015614/TEST/及时撤单/orderMoney1000000_timeInterval60.pkl'
withdraw_df = pd.read_pickle(withdraw_path)

europa_profit_df_fpath = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5'
europa_profit_df = pd.read_hdf(europa_profit_df_fpath)
europa_profit_df['datelist'] = europa_profit_df.index.get_level_values(0).strftime('%Y%m%d').map(int)
europa_profit_df = europa_profit_df.query('20220518 <= datelist <= 20230518')

withdraw_df['is_withdraw'] = 1 - withdraw_df['is_withdraw'].fillna(0)

concat_df = pd.concat(europa_profit_df, )