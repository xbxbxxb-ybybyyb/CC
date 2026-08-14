import numpy as np
import pandas as pd
#
# 上涨过程中的最大回撤，zcz/2
# gg
#
# zcz
factor_name = 'factor_qyh_tick_md'#
def factor_qyh_tick_md(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.02}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    if not tick_df.empty:
        lastpx = np.array(tick_df['LastPx']/pre_close-1)
        lastpx = lastpx / 2 if zcz else lastpx
        if len(lastpx)>1:
            res = []
            for i in range(len(lastpx)):
                min_i = lastpx[i:].min()
                res.append(min_i - lastpx[i])
            res = np.array(res).min()
        else:
            res = 0
    else:
        res = 0
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
