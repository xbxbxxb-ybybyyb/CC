import numpy as np
import pandas as pd
# 所属行业股票在T日的日内涨跌幅均值
#
factor_name = 'qyh_marketindttick_test'#
def factor_qyh_marketindttick_test(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # tick_df = tick_df.groupby(['dt','Ticker']).nth([0,-1])
    res = tick_df.groupby(['dt', 'Ticker']).nth([0, -1])['LastPx'].groupby(['dt', 'Ticker']).apply(
        lambda x: x[1] / x[0] if len(x) == 2 else 1)
    res = res.mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)