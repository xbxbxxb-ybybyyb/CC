# coding: utf-8
# Author：fengchi863
# Date ：2024/11/7 8:42

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
from LucienUtil.SpeedUtil import SpeedUtil
import os
import zipfile
from tqdm import tqdm
import shutil
from xquant.thirdpartydata.marketdata import MarketData

md = MarketData()
fd = FactorData()

def get_stk_list(_date):
    df = fd.get_factor_value('Basic_factor', mddate=[str(_date)], factor_names=['pre_close']).iloc[:, 0].unstack()
    stk_list = df.columns.tolist()
    return stk_list


def save_data(stk_code_list, dat, md):
    for stk_code in tqdm(stk_code_list):
        print(stk_code)
        tick_df = md.getMDSecurityTickDataFrame(stk_code, f"{dat}090000", f"{dat}160000", 1)
        if tick_df.shape[0] == 0:
            continue
        else:
            tick_df = tick_df.sort_values(by=['MDTime'])
        # tick_df.nunique(axis=0)
        rename_dict = {'MDDate': 'MDDate',
                       'MDTime': 'MDTime',
                       # 'SecurityType', # 产品大类，不使用
                       # 'SecurityID',   # 证券代码，用下面华泰的加上后缀的
                       # 'Symbol',   # 证券名称
                       'PreClosePx': 'pre_close', # 昨收价，全天唯一
                       'NumTrades': 'trade_nums',
                       'TotalVolumeTrade': 'volume_sum',
                       'TotalValueTrade': 'value_sum',
   
                       'LastPx': 'last_px',
                       'OpenPx': 'open_px',
                       'HighPx': 'high_px',
                       'LowPx': 'low_px',
                       'MaxPx': 'max_px',
                       'MinPx': 'min_px',
   
                       'WeightedAvgBidPx': 'weight_bid_vwap',
                       'WeightedAvgOfferPx': 'weight_offer_vwap',
   
                       # 'TotalBidNumber', # 这两个都是唯一值，没有用的字段
                       # 'TotalOfferNumber',   # 这两个都是唯一值，没有用的字段
   
                       'TotalBidQty': 'bid_qty_sum',
                       'TotalOfferQty': 'offer_qty_sum',
   
                       'Buy1Price': 'buy1_px',
                       'Buy1OrderQty': 'buy1_order_qty',
                       'Sell1Price': 'sell1_px',
                       'Sell1OrderQty': 'sell1_order_qty',
                       'Buy1NumOrders': 'buy1_order_num',
                       'Sell1NumOrders': 'sell1_order_num',
                       'Buy2Price': 'buy2_px',
                       'Buy2OrderQty': 'buy2_order_qty',
                       'Sell2Price': 'sell2_px',
                       'Sell2OrderQty': 'sell2_order_qty',
                       'Buy2NumOrders': 'buy2_order_num',
                       'Sell2NumOrders': 'sell2_order_num',
                       'Buy3Price': 'buy3_px',
                       'Buy3OrderQty': 'buy3_order_qty',
                       'Sell3Price': 'sell3_px',
                       'Sell3OrderQty': 'sell3_order_qty',
                       'Buy3NumOrders': 'buy3_order_num',
                       'Sell3NumOrders': 'sell3_order_num',
                       'Buy4Price': 'buy4_px',
                       'Buy4OrderQty': 'buy4_order_qty',
                       'Sell4Price': 'sell4_px',
                       'Sell4OrderQty': 'sell4_order_qty',
                       'Buy4NumOrders': 'buy4_order_num',
                       'Sell4NumOrders': 'sell4_order_num',
                       'Buy5Price': 'buy5_px',
                       'Buy5OrderQty': 'buy5_order_qty',
                       'Sell5Price': 'sell5_px',
                       'Sell5OrderQty': 'sell5_order_qty',
                       'Buy5NumOrders': 'buy5_order_num',
                       'Sell5NumOrders': 'sell5_order_num',
                       'Buy6Price': 'buy6_px',
                       'Buy6OrderQty': 'buy6_order_qty',
                       'Sell6Price': 'sell6_px',
                       'Sell6OrderQty': 'sell6_order_qty',
                       'Buy6NumOrders': 'buy6_order_num',
                       'Sell6NumOrders': 'sell6_order_num',
                       'Buy7Price': 'buy7_px',
                       'Buy7OrderQty': 'buy7_order_qty',
                       'Sell7Price': 'sell7_px',
                       'Sell7OrderQty': 'sell7_order_qty',
                       'Buy7NumOrders': 'buy7_order_num',
                       'Sell7NumOrders': 'sell7_order_num',
                       'Buy8Price': 'buy8_px',
                       'Buy8OrderQty': 'buy8_order_qty',
                       'Sell8Price': 'sell8_px',
                       'Sell8OrderQty': 'sell8_order_qty',
                       'Buy8NumOrders': 'buy8_order_num',
                       'Sell8NumOrders': 'sell8_order_num',
                       'Buy9Price': 'buy9_px',
                       'Buy9OrderQty': 'buy9_order_qty',
                       'Sell9Price': 'sell9_px',
                       'Sell9OrderQty': 'sell9_order_qty',
                       'Buy9NumOrders': 'buy9_order_num',
                       'Sell9NumOrders': 'sell9_order_num',
                       'Buy10Price': 'buy10_px',
                       'Buy10OrderQty': 'buy10_order_qty',
                       'Sell10Price': 'sell10_px',
                       'Sell10OrderQty': 'sell10_order_qty',
                       'Buy10NumOrders': 'buy10_order_num',
                       'Sell10NumOrders': 'sell10_order_num',
                       'HTSCSecurityID': 'symbol',  # 华泰自定义，重命名
                       # 'ReceiveDateTime',  # 华泰接收到行情的时间，删除
                       }
        need_col = list(rename_dict.keys())
        tick_df = tick_df[need_col]

        tick_df = tick_df.rename(rename_dict, axis=1)

        year = dat[:4]
        year_month = dat[:6]

        output_dir = f'/data/user/015614/daily/data/Tick/{year}/{year_month}/{dat}/'
        os.makedirs(output_dir, exist_ok=True)
        tick_df.to_csv(output_dir + f'{stk_code}.csv', index=False)

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


date_list = fd.tradingday(20241201, 20241231)
for dat in date_list:
    stk_code_list = get_stk_list(dat)
    # save_data(stk_code_list, dat, md)
    # save_data(['600519.SH'], '20241106', md)
    # save_data(['000001.SZ'], '20241106', md)
    SpeedUtil.multiprocess(15, save_data, stk_code_list, dat, md)

    year = dat[:4]
    year_month = dat[:6]

    output_dir = f'/data/user/015614/daily/data/Tick/{year}/{year_month}/{dat}/' # NOTE: 千万不能改，后面有删除

    create_zip_with_max_compression(output_dir, f'/data/user/015614/daily/data/Tick/{year}/{year_month}/{dat}.zip')
    shutil.rmtree(output_dir)