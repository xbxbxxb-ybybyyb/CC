import numpy as np
import pandas as pd
factor_name = 'qyh_tick_conv'#
def factor_qyh_tick_conv(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.036}
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    for type in ['Buy','Sell']:
        tick_df[type + 'Qty4'] = 0
        for i in range(4):
            tick_df[type + 'Qty4'] += tick_df[type + str(i+1) + 'OrderQty']
        tick_df[type + 'Qty5'] = tick_df[type + 'Qty4'] + tick_df[type + '5OrderQty']
        tick_df[type + 'Qty10'] = 0
        for i in range(10):
            tick_df[type + 'Qty10'] += tick_df[type + str(i+1) + 'OrderQty']
    tick_df['slob1'] = (tick_df['Buy4Price'] - tick_df['Buy1Price']) / pre_close / \
            ((tick_df['BuyQty4'] - tick_df['Buy1OrderQty']) / tick_df['BuyQty10'])
    tick_df['slob2'] = (tick_df['Buy10Price'] - tick_df['Buy5Price']) / pre_close / \
            ((tick_df['BuyQty10'] - tick_df['BuyQty5']) / tick_df['BuyQty10'])
    tick_df['slos1'] = (tick_df['Sell4Price'] - tick_df['Sell1Price']) / pre_close / \
            ((tick_df['SellQty4'] - tick_df['Sell1OrderQty']) / tick_df['SellQty10'])
    tick_df['slos2'] = (tick_df['Sell10Price'] - tick_df['Sell5Price']) / pre_close / \
            ((tick_df['SellQty10'] - tick_df['SellQty5']) / tick_df['SellQty10'])
    res1 = ((tick_df['slob1'] + tick_df['slos1']) / (tick_df['slos1'] - tick_df['slob1'])).mean()
    res2 = ((tick_df['slob2'] + tick_df['slos2']) / (tick_df['slos2'] - tick_df['slob2'])).mean()
    factor_dict = {factor_name: res1 + res2} # -0.09,37
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
