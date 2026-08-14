# coding: utf-8
# Author：fengchi863
# Date ：2022/4/19 18:10

from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
import numpy as np
import pandas as pd
from SimiStock.dataApi import stockList, tradeDate
import os

os.system(f'python3 {code_root_path}DataPrepare/get_clean_stock.py')
print('已更新clean_stock')
os.system(f'python3 {code_root_path}DataPrepare/get_rong_data.py')
print('已更新2rong')


def trans_str(tmp):
    if type(tmp) is str and not (str(tmp).endswith('SZ') or str(tmp).endswith('SH')):
        tmp = int(tmp)
    elif type(tmp) is str:
        tmp = stockList.trans_windcode2int(tmp)
    return tmp


if __name__ == '__main__':
    today_date = tradeDate.get_today(dividing_point=6)
    pre_date = tradeDate.get_pre_trade_date(today_date)
    code_list = np.load(barra_path2 + 'code_list.npy')
    block_data = pd.read_excel(f'大宗标的清单{str(today_date % 10000).zfill(4)}.xlsx', sheet_name='Sheet1', index_col=0)
    block_data.index = block_data.index.map(lambda x: trans_str(x))
    block_data = block_data.reset_index(drop=True)
    block_data = block_data.drop_duplicates(['证券代码'])
    block_data.columns = ['股票代码', '股票名称']
    block_data = block_data.set_index(['股票代码'], drop=True)
    block_data.index = block_data.index.map(stockList.trans_windcode2int)
    util.save_df2pkl(block_data, tracking_path, f'{today_date}_block_data.pkl')

    block_data = block_data.drop(set(block_data.index).difference(set(code_list)))

    # 是否区分区别
    old_block_data = pd.read_pickle(tracking_path + f'{pre_date}_block_data.pkl')
    new_bd = list(set(block_data.index).difference(set(old_block_data.index)))
    delete_bd = list(set(old_block_data.index).difference(block_data.index))
    print('新增的个股有：', ', '.join(map(str, new_bd)))
    print('删除的个股有：', ', '.join(map(str, delete_bd)))
    block_data = block_data.loc[new_bd]

    block_data = block_data.reset_index()
    block_data['交易日期'] = today_date
    block_data['折价比例'] = 0.5
    util.save_df2pkl(block_data, data_path, 'recent_block_data.pkl')
    #
    # check = pd.read_pickle(tracking_path + '20220415_block_data.pkl')
    # old_list = check['股票代码'].tolist()
    # new_list = block_data.index.tolist()
    # a = list(set(new_list).difference(set(old_list)))