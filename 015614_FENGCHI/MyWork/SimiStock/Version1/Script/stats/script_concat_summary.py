# coding: utf-8
# Author：fengchi863
# Date ：2022/3/18 8:54

import pandas as pd
from SimiStock.config.path_config import *
from SimiStock.SimiStockGenerator.util import util


if __name__ == '__main__':
    ret_df = pd.DataFrame()
    # summary_result = [f'final_summary{i}.xlsx' for i in range(1, 13)]
    summary_result = [f'{i}_txTest.xlsx' for i in range(1, 6)]
    for summary in summary_result:
        tmp = pd.read_excel(bt_path + summary, index_col=0)
        ret_df = pd.concat([ret_df, tmp], axis=0)
    util.save_df2xls(ret_df, bt_summary_path, 'tx_Test汇总.xlsx')
