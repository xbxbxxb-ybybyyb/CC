import numpy as np
import pandas as pd
factor_name = 'qyh_tick_b12b_mm_a2'#
def factor_qyh_tick_b12b_mm_a2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.08}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['b12b'] = tick_df['Buy1Price'] - tick_df['WeightedAvgBidPx']
    tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    tick_df1['b12b'] = tick_df1['Buy1Price'] - tick_df1['WeightedAvgBidPx']
    tick_df1['b12b'] += tick_df1['b12b'].min()
    tick_df2['b12b'] = tick_df2['Buy1Price'] - tick_df2['WeightedAvgBidPx']
    tick_df2['b12b'] += tick_df2['b12b'].min()
    res1 = tick_df1['b12b'].max() / tick_df1['b12b'].mean() if tick_df1['b12b'].mean()>0 else np.nan
    res2 = tick_df2['b12b'].max() / tick_df2['b12b'].mean() if tick_df2['b12b'].mean() > 0 else np.nan
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)