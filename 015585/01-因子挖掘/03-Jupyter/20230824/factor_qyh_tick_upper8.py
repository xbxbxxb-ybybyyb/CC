import numpy as np
import pandas as pd
#
# 上穿8%的次数，若0次（高开），则记为1次
# 0.08,20,重复值高
factor_name = 'qyh_tick_upper8'#
def factor_qyh_tick_upper8(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2}
    pre_close = tick_df['pre_close'].values[0]
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    limit_8 = pre_close * 1.14 if zcz else pre_close * 1.07
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[(tick_df['LastPx'].shift(1) < limit_8) & (tick_df['LastPx'] > limit_8)]
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
    tick_df['MDTime_delta'] = tick_df['MDTime'].apply(lambda x : inttime2deltamls(x))
    res = len(tick_df[tick_df['MDTime_delta'] - tick_df['MDTime_delta'].shift(1) > 60000])
    res = 1 if res == 0 else res
    res = 10 if res > 10 else res
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
