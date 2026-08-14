# coding: utf-8
# Author：fengchi863
# Date ：2024/11/6 14:37

# coding: utf-8
# Author：fengchi863
# Date ：2024/11/5 16:46

import pandas as pd
import numpy as np
from xquant.marketdata import MarketData
from xquant.factordata import FactorData
from LucienUtil.SpeedUtil import SpeedUtil
import os
import zipfile
from tqdm import tqdm
import shutil

md = MarketData()
fd = FactorData()

def get_stk_list(_date):
    df = fd.get_factor_value('Basic_factor', mddate=[str(_date)], factor_names=['pre_close']).iloc[:, 0].unstack()
    stk_list = df.columns.tolist()
    return stk_list


def save_data(stk_code_list, dat, md):
    for stk_code in tqdm(stk_code_list):
        print(stk_code)
        order_df = md.get_data_by_date('Order', stk_code, dat)
        if order_df.shape[0] == 0:
            continue
        else:
            order_df = order_df.sort_values(by=['MDTime', 'OrderIndex'])
        # order_df.nunique(axis=0)
        need_col = ['MDDate',
                    'MDTime',
                    # 'SecurityID',   # 证券代码，用下面华泰的加上后缀的
                    # 'Symbol',   # 证券名称
                    'OrderIndex',
                    'OrderType',  # 为1表示撤单，深圳才有
                    'OrderBSFlag',  # 华泰自定义，重命名
                    'OrderPrice',
                    'OrderQty',
                    'HTSCSecurityID',  # 华泰自定义，重命名
                    # 'ReceiveDateTime',  # 华泰接收到行情的时间，删除
                    ]
        if 'ChannelNo' in order_df.columns.tolist():
            need_col += ['ChannelNo', 'ApplSeqNum', 'OrderNO']
            rename_dict = {
                'TradeBSFlag': '委托方向',
                'HTSCSecurityID': '证券代码',
                'MDDate': '日期',
                'MDTime': '时间',
                'OrderIndex': '委托编号',
                'OrderType': '委托类别',
                'OrderPrice': '委托价格',
                'OrderQty': '委托数量',

                'ChannelNo': '原始频道',
                'ApplSeqNum': '原始记录号',
                'OrderNO': '原始订单号'
            }
        else:
            rename_dict = {
                'TradeBSFlag': '委托方向',
                'HTSCSecurityID': '证券代码',
                'MDDate': '日期',
                'MDTime': '时间',
                'OrderIndex': '委托编号',
                'OrderType': '委托类别',
                'OrderPrice': '委托价格',
                'OrderQty': '委托数量',
            }
        order_df = order_df[need_col]

        order_df = order_df.rename(rename_dict, axis=1)

        year = dat[:4]
        year_month = dat[:6]

        output_dir = f'/data/user/015614/daily/data/Order/{year}/{year_month}/{dat}/'
        os.makedirs(output_dir, exist_ok=True)
        order_df.to_csv(output_dir + f'{stk_code}.csv', index=False)

def create_zip_with_max_compression(source_path, destination_path):
    if not os.path.exists(source_path):
        print(f"Error: {source_path} does not exist.")

    with zipfile.ZipFile(destination_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.setpassword(b'258456')
        if os.path.isfile(source_path):
            zipf.write(source_path, os.path.basename(source_path))
        elif os.path.isdir(source_path):
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                    zipf.write(file_path, arcname)
        else:
            print(f"Error: {source_path} is not a valid file or directory.")


date_list = fd.tradingday(20160101, 20161231)
for dat in date_list:
    stk_code_list = get_stk_list(dat)
    # save_data(stk_code_list, dat, md)
    SpeedUtil.multiprocess(15, save_data, stk_code_list, dat, md)

    year = dat[:4]
    year_month = dat[:6]

    output_dir = f'/data/user/015614/daily/data/Order/{year}/{year_month}/{dat}/' # NOTE: 千万不能改，后面有删除

    create_zip_with_max_compression(output_dir, f'/data/user/015614/daily/data/Order/{year}/{year_month}/{dat}.zip')
    shutil.rmtree(output_dir)