import numpy as np
import pandas as pd
# zcz,
# 买1价在开盘3min和触发前3min的集中度差异
#
#
factor_name = 'qyh_ttick_20231012_8'#
def factor_qyh_ttick_20231012_8(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.02}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df['factor'] = tick_df['Buy1Price'] / pre_close
    if zcz:
        tick_df['factor'] = (tick_df['factor']-1)/2+1
    tick_df1 = tick_df.head(200)
    tick_df2 = tick_df.tail(60)
    para = 2
    res1 = (tick_df1['factor']**para).sum() / (tick_df1['factor'].sum()**para) #22，0.063 取200
    res2 = (tick_df2['factor']**para).sum() / (tick_df2['factor'].sum()**para) #65，-0.118 取60
    #
    factor_dict = {factor_name: res1*0.5-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
