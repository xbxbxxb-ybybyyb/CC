import pandas as pd

def factor_fc_o2pre(transaction_df, return_fillna_dic=False):
    factor_name = 'fc_o2pre'

    if return_fillna_dic:
        return {factor_name: 0}
    transaction_df = transaction_df[(transaction_df['TradePrice'] > 0)]  # 去除撤单
    transaction_df = transaction_df[transaction_df['MDTime'] < 93000000]

    try:
        ret = transaction_df.iloc[-1]['TradePrice'] / transaction_df.iloc[-1]['pre_close'] - 1
    except:
        ret = 0

    if transaction_df.shape[0] == 0:
        ret = 0
    else:
        dt, Ticker = transaction_df.index[0]
        zcz = (Ticker[0].startswith('3') and dt.strftime('%Y%m%D') >= "20200824") or (Ticker.startswith('68'))
        if zcz:
            ret /= 2

    factor = ret
    factor_dict = {factor_name: factor}

    return pd.Series(factor_dict)