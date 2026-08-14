import numpy as np
import pandas as pd
# zcz,dtj
#
#
#
factor_name = 'qyh_ttick_20231019_wj'#
def factor_qyh_ttick_20231019_wj(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    para = 400
    tick_df = tick_df.tail(para) if len(tick_df)>para else tick_df.tail(int(len(tick_df)/2))
    tick_df = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.25)]
    ret_pct = (tick_df['LastPx'] / tick_df['pre_close']-1)
    # ret_pct = ret_pct.apply(lambda x : x+0.001 if x == 0 else x)
    # res1 = 1/(1/ret_pct).sum()
    res = ret_pct.mean() / (abs(ret_pct - ret_pct.mean()).mean()+0.0001)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
