import numpy as np
import pandas as pd
#
#
# 55，-0.076
# xly_t_tick_xa15：38
factor_name = 'qyh_ttick_20231102_1'#
def factor_qyh_ttick_20231102_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -2}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df['factor'] = (tick_df['HighPx'] - tick_df['LowPx'])/pre_close
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    tick_df = tick_df.tail(100)
    res = tick_df['factor'].std() / (tick_df['factor'].mean()+1e-5)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
#
import numpy as np
import pandas as pd
#
#
# 85,-0.126 # 填充值用-2可以另一组；去掉除以std可以86;tick_df = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1)]为58不高相关
# qyh_ttick_20231019_1等5个
factor_name = 'qyh_ttick_20231102_1'#
def factor_qyh_ttick_20231102_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.67}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.25)]
    tick_df['factor'] = (tick_df['HighPx'] - tick_df['LowPx'])/pre_close
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    para = 150
    tick_df = tick_df.tail(para) if len(tick_df)>para else tick_df.tail(int(len(tick_df)/2))
    res = tick_df['factor'].std() / (tick_df['factor'].mean()+1e-5)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

import numpy as np
import pandas as pd
# zcz,dtj
# 最后100单金额
# 90.75
#
factor_name = 'qyh_ttrans_20231102_1'#
def factor_qyh_ttrans_20231102_1(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 4.2}
    #
    dt, ticker = trans_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = trans_df['pre_close'].values[0]
    mv = pre_close * trans_df['ff_shares'].values[0]
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
    trans_df = trans_df[trans_df['MDTime_delta'] >= t - 1000*5]
    trans_df = trans_df[trans_df['TradeBSFlag'] == 1]
    trans_df = trans_df[trans_df['TradePrice'] >= p_zt]
    res_df = trans_df.groupby('TradeBuyNo').sum()['TradeMoney']
    res_df = res_df[res_df>=50000]
    # res = trans_df['TradeMoney'].sum() / mv
    # res = trans_df['TradeMoney'].sum()
    res = res_df.sum()/mv
    if res == 0:
        res = 0.36
    if t <= 1810000:
        res = 0
    factor_dict = {factor_name: res}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)


