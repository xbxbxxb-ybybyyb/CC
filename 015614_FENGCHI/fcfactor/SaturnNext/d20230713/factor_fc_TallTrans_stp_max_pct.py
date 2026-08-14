# coding: utf-8
# Author：fengchi863
# Date ：2023/7/5 16:07

import pandas as pd
import datetime as dt

def factor_fc_TallTrans_stp_max_pct(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}
    dt, Ticker = df.index[0]
    df = df[(df['TradePrice'] > 0) & (df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
    df = df[df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据
    df['m'] = df['MDTime'] // 100000

    if len(df) == 0:
        return pd.Series({factor_name: 0})
    else:
        pre_close = df.iloc[0]['pre_close']

        df_low = df[df['TradeQty'] <= df['TradeQty'].quantile(0.3)]

        factor = ((df_low['TradePrice'] - df_low['TradePrice'].min()) / pre_close).max()

        factor_dict = {factor_name: factor}
    # print(factor_name, dt.strftime('%Y%m%d'), factor)
    # ----------------------------T日小单部分成交价格相对于最低价的最大值（负向，涨的越多，收益越低） 16.62 -5.47-------------------------------
    return pd.Series(factor_dict)
