# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
#
#
# 上涨时候的涨幅*量
# 0,0
def factor_qyh_talltick_pv_mean_up(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_pv_mean_up'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 30473}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    tick_df1 = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]
    # tick_df2 = tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]
    pv1 = ((tick_df1['LastPx'] / tick_df1['pre_close'].max() - 1) * tick_df1['VolumeTrade']).sum()
    # pv2 = ((tick_df2['LastPx'] / tick_df2['pre_close'].max() - 1) * tick_df2['VolumeTrade']).sum()
    if zcz:
        pv1 = pv1/2
        # pv2 = pv2/2
    factor_dict = {factor_name: pv1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

