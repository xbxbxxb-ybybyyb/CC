# coding: utf-8
# Author：fengchi863
# Date ：2022/1/11 9:34

import numpy as np
import pandas as pd

from FaaMonitor.Util.MyUtil import MyUtil


def generate_df(stk_list):
    ret = pd.DataFrame(index=stk_list)
    ret['股票名称'] = ret.index.map(lambda x: MyUtil.get_1stock_name(x))
    return ret

from ShortTermTrading.Util.tools import save_xlsx
from ShortTermTrading.conf.path_conf import junk_path

gdbd_df = pd.read_excel(junk_path + '该跌不跌每日股票池.xlsx', index_col=0)
check_df = gdbd_df.loc[20220106]

dealer_df = pd.read_excel(junk_path + 'GDBD20220106.xlsx', index_col=0)
dealer_df.index = dealer_df.index.map(lambda x: int(x[2:]))

check_stk_list = check_df['股票代码'].tolist()
dealer_stk_list = dealer_df.index.tolist()

our_stk_list = check_stk_list
their_stk_list = dealer_stk_list
only_in_our_stk_list = list(set(check_stk_list).difference(set(dealer_stk_list)))
only_in_their_stk_list = list(set(dealer_stk_list).difference(set(check_stk_list)))
common_stk_list = list(set(check_stk_list).intersection(set(dealer_stk_list)))

ret = dict()
ret['ours'] = generate_df(our_stk_list)
ret['dealers'] = generate_df(their_stk_list)
ret['only_in_ours'] = generate_df(only_in_our_stk_list)
ret['only_in_dealers'] = generate_df(only_in_their_stk_list)
ret['common'] = generate_df(common_stk_list)

with pd.ExcelWriter(junk_path + '该跌不跌股票池差异20220106.xlsx') as writer:
    for each in ret:
        ret[each].to_excel(writer, each)

print('====================')
print('ours', len(our_stk_list))
print('dealers', len(their_stk_list))
print('only_in_ours', len(only_in_our_stk_list))
print('only_in_dealers', len(only_in_their_stk_list))
print('common', len(common_stk_list))
print('====================')
