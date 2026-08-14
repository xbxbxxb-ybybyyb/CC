import numpy as np
import pandas as pd
# zcz,dtj
# 逻辑：买1的离群程度
# 85
#
factor_name = 'qyh_ttick_b1_m2m'#
def factor_qyh_ttick_b1_m2m(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:1.07}
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
    if len(tick_df[tick_df['MDTime'] >= 93000000]) > 20:
        tick_df = tick_df[tick_df['MDTime'] >= 93000000]
        tick_df['Buy1Price'] = tick_df['Buy1Price'] / pre_close
        if zcz:
            tick_df['Buy1Price'] = (tick_df['Buy1Price'] - 1)/2 + 1
        tick_df['Buy1Price'] = tick_df['Buy1Price'] + 0.5*tick_df['Buy1Price'].min()
        res = tick_df['Buy1Price'].max() / tick_df['Buy1Price'].mean() if round_(tick_df['Buy1Price'].mean(),5)>0 else np.nan
    else:
        res = 1.0496 - len(tick_df[tick_df['MDTime'] >= 93000000]) * 0.0001
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
