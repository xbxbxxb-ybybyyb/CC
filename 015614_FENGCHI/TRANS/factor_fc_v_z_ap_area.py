# coding: utf-8
# Author：fengchi863
# Date ：2023/3/13 12:04

# coding: utf-8
# Author：fengchi863
# Date ：2023/3/13 10:50
"""
price在日内vwap均线上方和下方的总面积
"""
import pandas as pd

#TTransaction(逐笔成交类因子)示例 Todo:注意TTransaction类因子需要控制低耗时
def factor_fc_v_z_ap_area(transaction_df, return_fillna_dic=False):
    factor_name = 'fc_v_z_ap_area'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df=transaction_df[transaction_df['TradePrice']>0] #去除深圳撤单的逐笔成交数据
    transaction_df = transaction_df[transaction_df['MDTime'] >=93000000] #选择连续竞价阶段的逐笔成交数据
    vwap = transaction_df.expanding()['TradeMoney'].sum() / transaction_df.expanding()['TradeQty'].sum()
    v_z_area = (transaction_df['TradePrice'] / vwap - 1).map(abs).sum()  # 未考虑CYB，未考虑ZT_Time量纲去除
    factor_dict = {factor_name: v_z_area}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

if __name__ == '__main__':
    import IO
    start_date, end_date=20160101, 20181231
    factor_df=factor_fc_v_z_ap_area(start_date,end_date,IO)
    factor_path = '/data/user/015614/factor/'
    factor_df.to_hdf(factor_path + 'fc_v_z_ap_area.h5', key='fc_v_z_ap_area', mode='w')
    print(factor_df.describe())