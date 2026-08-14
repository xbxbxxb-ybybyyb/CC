import numpy as np
import pandas as pd
# dtj
# 买1-买均偏离度在不同成交量下的差异
# -0.08,41
#
#
factor_name = 'qyh_tick_b12b_mm_a2'#
def factor_qyh_tick_b12b_mm_a2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.08}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
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

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
