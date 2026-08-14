import numpy as np
import pandas as pd

factor_name = 'qyh_ttick_bp_kurt'#
def factor_qyh_ttick_bp_kurt(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:15} # -0.079
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['ValueTrade'] = tick_df['ValueTrade'].apply(lambda x : round_(x,5))
    if zcz:
        tick_df['WeightedAvgBidPx'] = (tick_df['WeightedAvgBidPx']/ pre_close - 1)/2
    else:
        tick_df['WeightedAvgBidPx'] = tick_df['WeightedAvgBidPx'] / pre_close - 1
    tick_df['WeightedAvgOfferPx'] = tick_df['WeightedAvgOfferPx'].apply(lambda x:round_(x,5))
    res = tick_df['WeightedAvgBidPx'].kurt()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
