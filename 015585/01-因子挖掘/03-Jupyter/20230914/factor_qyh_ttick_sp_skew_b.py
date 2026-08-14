import numpy as np
import pandas as pd
# zcz
# 逻辑：成交量大的时候卖均偏度
#
#
factor_name = 'qyh_ttick_sp_skew_b'#
def factor_qyh_ttick_sp_skew_b(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:1.313}
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
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['VolumeTrade'].apply(lambda x : round_(x,5))
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    if zcz:
        tick_df['newPx'] = ((tick_df['Buy1Price'] + tick_df['Sell1Price'])/2/ pre_close - 1)/2
    else:
        tick_df['newPx'] = (tick_df['Buy1Price'] + tick_df['Sell1Price'])/2 / pre_close - 1
    tick_df['newPx'] = tick_df['LastPx'].apply(lambda x:round_(x,5))
    tick_df = tick_df[tick_df['VolumeTrade'] >= tick_df['VolumeTrade'].quantile(0.6)]
    #
    res = tick_df['newPx'].skew()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
