import numpy as np
import pandas as pd
#
# 小单的vwap
#
factor_name = 'qyh_trans_lit_vwap'#
def factor_qyh_trans_lit_vwap(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.1}
    pre_close = trans_df['pre_close'].values[0]
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    trans_df = trans_df[trans_df['TradePrice'] > 0]
    # trans_df['min'] = trans_df['MDTime'].apply(lambda x : int(x/100000))
    # # buy = buy[buy['TradeMoney'] <= 50000]
    # twap = trans_df.groupby('min').mean()['TradePrice'] / pre_close - 1
    # buy =  trans_df.groupby('min').sum()[['TradeMoney','TradeQty']]
    vwap = trans_df['TradeMoney'].cumsum() / trans_df['TradeQty'].cumsum() / pre_close - 1
    res = vwap.tail(1000).mean() if len(vwap)>1000 else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
