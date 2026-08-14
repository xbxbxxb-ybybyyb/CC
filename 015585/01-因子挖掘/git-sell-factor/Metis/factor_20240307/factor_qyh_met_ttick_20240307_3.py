import numpy as np
import pandas as pd
factor_name = 'qyh_met_ttick_20240307_3'#
def factor_qyh_met_ttick_20240307_3(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    import decimal
    def round_(x, n=0):
        x = x + 1e-10
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    tick_df['ValueTrade'] = (tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)).apply(lambda x : round_(x,5))
    tick_df['VolumeTrade'] = (tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)).apply(lambda x : round_(x,5))
    #
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    t_fzt = tick_df[tick_df['LastPx'] >= round_(tick_df['LastPx'].max()-0.01,2)]['MDTime'].min() # 首次逼近涨停时间
    tick_df = tick_df[tick_df['MDTime'] >= t_fzt]
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] >= round_(tick_df['ValueTrade'].quantile(0.75),2)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.25),2)]
    res = tick_df1['ValueTrade'].std() - tick_df2['ValueTrade'].std()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)