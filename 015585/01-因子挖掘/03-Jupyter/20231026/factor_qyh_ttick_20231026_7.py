import numpy as np
import pandas as pd
# zcz,dtj
# 最后20min里,最大pct_chg的相对量的中位数
# 70,0.1
#
factor_name = 'qyh_ttick_20231026_7'#
def factor_qyh_ttick_20231026_7(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.08}
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
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[(tick_df['ValueTrade'] >= round_(tick_df['ValueTrade'].quantile(0.5),2))]
    if tick_df.empty:
        res = -0.07
    else:
        if len(tick_df)<=20:
            tick_df = tick_df.tail(int(len(tick_df)/3))
        elif len(tick_df)<=100:
            tick_df = tick_df.tail(13)
        elif len(tick_df)<=600:
            tick_df = tick_df.tail(80)
        else:
            tick_df = tick_df.tail(400)
        tick_df['factor'] = tick_df['LastPx'].cummax() / pre_close -1
        if zcz:
            tick_df['factor'] = tick_df['factor']/2
        res = (tick_df['factor'] - tick_df['factor'].quantile(0.95)).quantile(0.5)
    factor_dict = {factor_name: res}
    return pd.Series(factor_dict)