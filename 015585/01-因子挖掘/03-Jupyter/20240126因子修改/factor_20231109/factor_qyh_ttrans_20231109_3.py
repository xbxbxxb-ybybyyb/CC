import numpy as np
import pandas as pd
# dtj,zcz
# 成交价格在8%以上的笔数比例
# 51,0.08
factor_name = 'qyh_ttrans_20231109_3'#
def factor_qyh_ttrans_20231109_3(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.06}
    #
    dt, ticker = trans_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = trans_df['pre_close'].values[0]
    # mv = pre_close * trans_df['ff_shares'].values[0]
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.16 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.08 + 0.5) / 100
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    res1 = len(trans_df.query(f'TradePrice >= {p_zt}'))
    res2 = len(trans_df)+1
    factor_dict = {factor_name: res1 / res2}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
