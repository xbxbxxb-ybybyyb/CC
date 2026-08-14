import numpy as np
import pandas as pd
#
# 价格凸性
#
factor_name = 'qyh_trans_conv'#
def factor_qyh_trans_conv(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    pre_close = trans_df['pre_close'].values[0]
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    trans_df = trans_df[trans_df['TradePrice'] > 0]
    trans_df['TradePrice'] = trans_df['TradePrice'] / pre_close -1
    def inttime2deltamls(itime):
        mls = int(str(int(itime))[-3:])
        s = int(str(int(itime))[-5:-3])
        m = int(str(int(itime))[-7:-5])
        h = int(str(int(itime))[:-7])
        time_mls = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + mls
        time_mls_930 = 9 * 3600 * 1000
        if int(itime) > 120000000:
            time_delta = time_mls - time_mls_930 - 5400000
        else:
            time_delta = time_mls - time_mls_930
        return time_delta
    trans_df['MDTime_delta'] = trans_df['MDTime'].apply(lambda x : inttime2deltamls(x))
    trans_df = trans_df.groupby('MDTime_delta').mean().reset_index()
    # trans_df['TradePrice_diff1'] = (trans_df['TradePrice'] - trans_df['TradePrice'].shift(1)) / \
    #                                (trans_df['MDTime_delta'] - trans_df['MDTime_delta'].shift(1))
    # trans_df['TradePrice_diff2'] = (trans_df['TradePrice_diff1'] - trans_df['TradePrice_diff1'].shift(1)) / \
    #                                (trans_df['MDTime_delta'] - trans_df['MDTime_delta'].shift(1))
    trans_df['TradePrice_diff2'] = (trans_df['TradePrice'] + trans_df['TradePrice'].shift(2) - 2*trans_df['TradePrice'].shift(1)) / \
                                   (trans_df['MDTime_delta'] - trans_df['MDTime_delta'].shift(1)) / (trans_df['MDTime_delta'] - trans_df['MDTime_delta'].shift(2))
    res = trans_df['TradePrice_diff2'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
