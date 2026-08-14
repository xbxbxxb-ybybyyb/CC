# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 已提交：0216
'''
逻辑：T日09:31数据，买卖双方力量对比(包括集合竞价）,
组合因子 = 买单的大单金额占比（49，0.1） + 买入每单金额/卖出每单金额(65,0.1) + 买入大单金额/卖出大单金额（39.4，0.1） - 买入小单金额/卖出小单金额(44.8,-0.08)
2-4不加权，分数71，0.09；加权，分数68
1和2相关性0.45，取2、3、4融合（53，0.1），3、4融合（56，0.1），1、4融合（56.3，0.11），2、3融合（66，0.109），1、3融合(67.5,0.11)
##最终选择2-4：从每单的强度、大小单的强度衡量买卖双方实力
##高CORR：wd_t1_up_med_bda：66.4；
wd_t1_down_vol_bda；pj2r_931_Buy_lengu_corr；sss_to1m_peramtb2s；wd_t1_no_act_bda；wd_cst1_big_bda_rank：39.3
##
factor_qyh_T1mtra_ratio_in_big
factor_qyh_T1mtra_power_inout_num
factor_qyh_T1mtra_power_inout_bigtotal
factor_qyh_T1mtra_power_inout_smalltotal
'''
# score:
factor_name = 'qyh_T1mtra_power_combo'
def factor_qyh_T1mtra_power_combo(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.09}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    # 买单的大单金额占比
    buy = transaction_df.groupby('TradeBuyNo').sum()['TradeMoney']

    # factor_1 = buy[buy >= 200000].sum() / buy.sum() if abs(buy.sum())>0.001 else np.nan
    # factor_1 = factor_1 / 0.295
    # 买入每单金额/卖出每单金额
    sell = transaction_df.groupby('TradeSellNo').sum()['TradeMoney']
    factor_2 = len(sell)/len(buy) if len(buy) != 0 else np.nan
    factor_2 = np.log(0.01) if factor_2 < 0.01 else np.log(factor_2) if factor_2 < 100 else np.log(100)
    # factor_2 = factor_2 / 1.77
    # 买入大单金额/卖出大单金额
    # factor_3 = buy[buy >= 200000].sum() / sell[sell >= 200000].sum() if abs(sell[sell >= 200000].sum()) >0.001 else np.nan
    # factor_3 = np.log(0.01) if factor_3 < 0.01 else np.log(factor_3) if factor_3 < 100 else np.log(100)
    # factor_3 = factor_3 / 0.6411
    # 买入小单金额/卖出小单金额
    factor_4 = buy[buy < 200000].sum() / sell[sell < 200000].sum() if abs(sell[sell < 200000].sum()) >0.001 else np.nan
    factor_4 = np.log(0.01) if factor_4 < 0.01 else np.log(factor_4) if factor_4 < 100 else np.log(100)
    # factor_4 = factor_4 / 1.808
    # combo
    factor = factor_2 - factor_4
    factor_dict = {factor_name: factor}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
