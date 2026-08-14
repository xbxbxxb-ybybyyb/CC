import numpy as np
import pandas as pd
#
# vwap变形
#
factor_name = 'qyh_tick_vwap'#
def factor_qyh_tick_vwap(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    pre_close = tick_df['pre_close'].values[0]
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')

    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    if len(tick_df) > 0:
        res = tick_df['TotalValueTrade'].tail(1).values[0] / tick_df['TotalBidQty'].max()
        res = res/pre_close-1
        res = res/2 if zcz else res
    else:
        res = np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
