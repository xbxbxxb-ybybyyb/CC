# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 10:15
# @Author  : qinyuhao

# 逻辑：计算20日涨跌幅，根据单笔成交金额的大小构成的理想反转因子
# score:4.4
# 废弃：用q后缀的因子代替，分位数取的越高，对return20的切割效果越好，用mean过于平庸
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_return_ideal_20'
def factor_qyh_return_ideal_20(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # 可修改的因子编写部分
    # 该部分与alpha因子计算方式一致，计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # 返回dt, Ticker格式multiindex的DataFrame, 一列，列名为因子名称
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])

    # 买单委托笔数，这里用买单委托笔数代替成交笔数
    g1_data = IO.read_data([start_date, end_date],
                           alt='/data/group/800463/data/generalStrong/ordersheet5/TotalBidQty.h5')
    # 成交额
    g2_data = IO.read_data([start_date, end_date],
                           alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    # 平均单笔成交额
    g_data = pd.DataFrame(g2_data.sum(axis=1) / g1_data.sum(axis=1), columns=['amt_avgorder'])
    del g1_data,g2_data
    f_data = IO.read_data([start_date, end_date],
                          columns=['pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # 单笔成交额取20日内排序，前一半为正，后一半为负
    import bottleneck as bn
    g_data_move20_rank = pd.DataFrame(bn.move_rank(g_data['amt_avgorder'].unstack(), window=20, min_count=10, axis=0),
                                      index=g_data['amt_avgorder'].unstack().index,
                                      columns=g_data['amt_avgorder'].unstack().columns)
    g_data_move20_rank = g_data_move20_rank.stack().apply(lambda x: 1 if x >= 0 else -1)
    # 将20日涨跌幅按单笔成交金额示性函数加权
    f_data[factor_name] = f_data['pct_chg'] * g_data_move20_rank
    f_data[factor_name] = f_data[factor_name].unstack().rolling(20, 10).mean().stack()#用mean而不是sum是因为有空值存在
    f_data = pd.DataFrame(f_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return f_data

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。