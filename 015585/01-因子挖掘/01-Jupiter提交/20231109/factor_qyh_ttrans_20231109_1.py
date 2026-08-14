import numpy as np
import pandas as pd
# dtj
# 最后100笔聚合后的买单均值/1000笔聚合后均值
# 47,0.1
factor_name = 'qyh_ttrans_20231109_1'#
def factor_qyh_ttrans_20231109_1(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.9}
    #
    # dt, ticker = trans_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre_close = trans_df['pre_close'].values[0]
    # mv = pre_close * trans_df['ff_shares'].values[0]
    # if zcz:
    #     p_zt = np.floor(pre_close * 100 * 1.18 + 0.5) / 100
    # else:
    #     p_zt = np.floor(pre_close * 100 * 1.09 + 0.5) / 100
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    trans_df1 = trans_df.tail(100)
    trans_df2 = trans_df.tail(1000)
    #
    res1 = trans_df1.groupby('TradeBuyNo').sum()['TradeMoney'].mean()
    res2 = trans_df2.groupby('TradeBuyNo').sum()['TradeMoney'].mean()
    factor_dict = {factor_name: res1/res2}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
