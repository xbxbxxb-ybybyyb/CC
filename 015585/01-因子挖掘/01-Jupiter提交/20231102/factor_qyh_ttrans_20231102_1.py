import numpy as np
import pandas as pd
factor_name = 'qyh_ttrans_20231102_1'#
def factor_qyh_ttrans_20231102_1(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 420867}
    #
    dt, ticker = trans_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = trans_df['pre_close'].values[0]
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.18 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.09 + 0.5) / 100
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    trans_df = trans_df[trans_df['TradeMoney'] > 0]
    #
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
    trans_df['MDTime_delta'] = trans_df['MDTime'].apply(
        lambda x: inttime2deltamls(x))
    t = trans_df['MDTime_delta'].max()
    trans_df = trans_df[trans_df['MDTime_delta'] >= t - 1000*30]
    trans_df = trans_df[trans_df['TradeBSFlag'] == 1]
    trans_df = trans_df[trans_df['TradePrice'] >= p_zt]
    res_df = trans_df.groupby('TradeBuyNo').sum()['TradeMoney']
    res_df = res_df[res_df>=50000]
    res = res_df.mean()
    factor_dict = {factor_name: res}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
