import numpy as np
import pandas as pd
# zcz,dtj
# 最前+最后20min里,最高价涨跌幅离散程度
# 65,0.098
#
factor_name = 'qyh_ttick_20231026_1'#
def factor_qyh_ttick_20231026_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -2}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['factor'] = (tick_df['HighPx'] / tick_df['pre_close']-1)
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    para = 400
    tick_df2 = tick_df.tail(para) if len(tick_df)>para else tick_df.tail(int(len(tick_df)/2))
    res2 = tick_df2['factor'].mean() / (tick_df2['factor'].std()+1e-5)
    #
    para3 = 400
    tick_df1 = tick_df.head(para3) if len(tick_df)>(para3*2)else tick_df.head(int(len(tick_df)/2))
    res1 = tick_df1['factor'].mean() / (tick_df1['factor'].std()+1e-5)
    factor_dict = {factor_name: res2 + res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
