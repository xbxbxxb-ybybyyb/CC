import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231102_2'#
def factor_qyh_torder_20231102_2(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    #
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = order_df['pre_close'].values[0]
    # mv = pre_close * order_df['ff_shares'].values[0]
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
    order_df['MDTime_delta'] = order_df['MDTime'].apply(
        lambda x: inttime2deltamls(x))
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    order_df = order_df[order_df['OrderPrice'] < p_zt]
    order_df1 = order_df[order_df['OrderBSFlag']==1]
    order_df1 = order_df1.head(int(len(order_df1)/2))
    order_df2 = order_df[order_df['OrderBSFlag']==2]
    order_df2 = order_df2.head(int(len(order_df2)/2))
    #
    res1 = order_df1['MDTime_delta'].sum() / (order_df1['MDTime_delta'].std() ** 0.8)
    res2 = order_df2['MDTime_delta'].sum() / (order_df2['MDTime_delta'].std() ** 0.8)
    factor_dict = {factor_name: res1/res2 if res2 > 0 else np.nan}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
