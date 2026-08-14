import numpy as np
import pandas as pd
# zcz
# 成交-买均的离群程度在开盘后和触发前的差
# 59,0.11
# 和已开发的高相关
factor_name = 'qyh_ttick_t2b_mm_h12'#
def factor_qyh_ttick_t2b_mm_h12(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['tp'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    tick_df['factor'] = (tick_df['tp'] - tick_df['WeightedAvgBidPx']) /\
                        pre_close
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    tick_df1 = tick_df.head(int(len(tick_df)/2)) if len(tick_df)>10 else tick_df
    res1 = tick_df1['factor'].max() / tick_df1['factor'].mean()
    tick_df2 = tick_df.tail(int(len(tick_df)/2)) if len(tick_df)>10 else tick_df
    res2 = tick_df2['factor'].max() / tick_df2['factor'].mean()
    #
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
