import numpy as np
import pandas as pd
# dtj
# 挂卖均价在不同成交量的变异系数
# -0.096,54
#
factor_name = 'qyh_tick_sp_cv_a2'#
def factor_qyh_tick_sp_cv_a2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.04}
    pre_close = tick_df['pre_close'].values[0]
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res

    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = tick_df['ValueTrade'].apply(lambda x:round_(x,5))
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df1 = tick_df[tick_df['ValueTrade'] >= round_(tick_df['ValueTrade'].quantile(0.85),5)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.15),5)]
    if (len(tick_df1) > 0) & (len(tick_df2) > 0):
        tick_df1['WeightedAvgOfferPx_new'] = tick_df1['WeightedAvgOfferPx'] / pre_close - 1
        tick_df2['WeightedAvgOfferPx_new'] = tick_df2['WeightedAvgOfferPx'] / pre_close - 1
        if (round_(abs(tick_df1['WeightedAvgOfferPx_new'].mean()),5) > 0) \
            & (round_(abs(tick_df2['WeightedAvgOfferPx_new'].mean()),5) > 0):
            res1 = tick_df1['WeightedAvgOfferPx_new'].std() / \
                   abs(tick_df1['WeightedAvgOfferPx_new'].mean())
            res2 = tick_df2['WeightedAvgOfferPx_new'].std() / \
                   abs(tick_df2['WeightedAvgOfferPx_new'].mean())
            res = res1-res2
        else:
            res = np.nan
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
