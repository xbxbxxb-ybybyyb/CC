import numpy as np
import pandas as pd
factor_name = 'qyh_tick_max_nottail15'#
def factor_qyh_tick_max_nottail15(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.063}
    import decimal
    def round_(x, n=0):
        x = x+1e-8
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    pre_close = tick_df['pre_close'].values[0]
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')

    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    length = 300
    if len(tick_df)>length:
        tick_df = tick_df.head(len(tick_df) - length)
        res = tick_df['LastPx'].max() / pre_close - 1
        res = res/2 if zcz else res
    else:
        res = tick_df[tick_df['LastPx'] < round_(tick_df['LastPx'].max()-0.01,5)]['LastPx'].max() / pre_close -1
        res = res / 2 if zcz else res
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
