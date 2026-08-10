import pandas as pd
import numpy as np
import datetime
import re
import os
import warnings
from xquant.marketdata import MarketData as XMD
from xquant.thirdpartydata.marketdata import MarketData as XMDTP
import multifactor.utility.common as ut
import multifactor.utility.dt as udt
from multifactor.IO import IO
from tqdm import tqdm
from multiprocessing import Pool
import dill
from multifactor.data.utils import *

def sh_order_checker(df_result, df_transaction, df_tick):
    """
    检查还原结果是否正确
    :param df_result: pd.DataFrame
        还原后的order数据
    :param df_transaction: pd.DataFrame
        上交所transaction数据
    :param df_tick: pd.DataFrame
        上交所tick数据
    :return: None
    """
    num = df_tick['TotalBidQty'].iloc[-1] + \
          df_tick['TotalOfferQty'].iloc[-1] + \
          df_result[df_result['OrderType'] == 10]['OrderQty'].sum() + \
          df_transaction['TradeQty'].sum() * 2 - \
          df_result[df_result['OrderType'] == 2]['OrderQty'].sum()
    assert np.isclose(num, 0)


def reform_sh_order(df_order, df_transaction, append_cancel_orders):
    if len(df_order) == 0 or len(df_transaction) == 0:
        return pd.DataFrame()
    # caution original index is ignored
    df_order_2 = df_order[df_order['OrderType'] == 2].copy()  # limit price order
    df_order_10 = df_order[df_order['OrderType'] == 10].copy()  # cancel order
    # transform pandas to dict to speed up record loc and modification
    df_order_2 = df_order_2.set_index(['OrderNO'])
    df_order_2 = df_order_2.T.to_dict(orient='series')
    for trans_rec in df_transaction.itertuples():
        if trans_rec.TradeBuyNo > trans_rec.TradeSellNo:
            order_no = trans_rec.TradeBuyNo
            order_bsflag = 1
        else:
            order_no = trans_rec.TradeSellNo
            order_bsflag = 2
        try:
            # if order exists in order dict, just modify price and quantity
            order_rec = df_order_2[order_no]
            if order_rec['OrderIndex'] == -1 or trans_rec.ApplSeqNum < order_rec['ApplSeqNum']:  # auction proof
                order_rec['OrderQty'] += trans_rec.TradeQty
                order_rec['OrderPrice'] = (max if order_bsflag == 1 else min)(order_rec['OrderPrice'],
                                                                              trans_rec.TradePrice)
        except KeyError:
            df_order_2[order_no] = pd.Series({'MDDate': trans_rec.MDDate,
                                              'MDTime': trans_rec.MDTime,
                                              'HTSCSecurityID': trans_rec.HTSCSecurityID,
                                              'OrderIndex': -1,  # not used in practice for SH
                                              'OrderType': 2,
                                              'OrderPrice': trans_rec.TradePrice,
                                              'OrderQty': trans_rec.TradeQty,
                                              'OrderBSFlag': order_bsflag,
                                              'ReceiveDateTime': trans_rec.ReceiveDateTime,
                                              'ApplSeqNum': trans_rec.ApplSeqNum})
    df_order_reformed = pd.DataFrame.from_dict(df_order_2, orient='index')
    df_order_reformed.index.name = 'OrderNO'
    df_order_reformed = df_order_reformed.reset_index()
    if append_cancel_orders:
        df_order_reformed = df_order_reformed.append(df_order_10, ignore_index=True, sort=False).sort_values(by='ApplSeqNum').reset_index(drop=True)
    else:
        df_order_reformed = df_order_reformed.sort_values(by='ApplSeqNum').reset_index(drop=True)
    return df_order_reformed


def format_datetime(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')


def get_level2_data(para, append_cancel_orders=True, save_root_path = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK_STOPPING/'):
    assert len(para) == 3 and isinstance(para[0], str) and isinstance(para[1], str)
    stock = para[0]
    date = para[1]
    dtype = para[2]
    assert dtype in ['Transaction', 'Order', 'Stock']

    try:
        md = XMD()
        mdtp = XMDTP()

        if dtype == 'Order':
            if '.SH' in stock:
                df_transaction = mdtp.getMDTransactionDataFrame(stock, date + '000000', date + '235959')
                df_order = mdtp.getMDOrderDataFrame(stock, date + '000000', date + '235959')
                df = reform_sh_order(df_order, df_transaction, append_cancel_orders=append_cancel_orders)
            else:
                df = mdtp.getMDOrderDataFrame(stock, date + '000000', date + '235959')
        elif dtype == 'Transaction':
            df = mdtp.getMDTransactionDataFrame(stock, date + '000000', date + '235959')
        elif dtype == 'Stock':
            df = md.get_data_by_date("Stock", stock, str(date))
        else:
            raise NotImplementedError

        del(md)
        del(mdtp)
    except:
        df = pd.DataFrame()

    if len(df) == 0:
        warnings.warn(f'{stock} {dtype} data does not exist at {date}')
        return (stock,df)

    df['dt'] = df.apply(lambda x: format_datetime(x.MDDate, x.MDTime), axis=1)
    # for Order
    if dtype == 'Order':
        droplist = ['MDDate', 'MDTime', 'HTSCSecurityID']
    elif dtype == 'Transaction':
        droplist = ['MDDate', 'MDTime', 'SecurityType', 'HTSCSecurityID']
    elif dtype == 'Stock':
        droplist = ['MDDate', 'MDTime', 'SecurityType', 'HTSCSecurityID', 'ReceiveDateTime', 'MDRecordID', 'MDReportID', 'MDStreamID', 'SecuritySubType',
                    'SecurityIDSource', 'Symbol', 'MDLevel', 'MDChannel', 'TradingPhaseCode', 'SwitchStatus', 'MDRecordType', 'MDValidType']
    else:
        droplist = []
    df = df.drop(droplist, axis=1)
    df['Ticker'] = stock
    df = df.set_index(['dt','Ticker'])
#     print(f'{stock} {dtype} data at {date} dumped successfully')
    if dtype == 'Stock':
        save_path = os.path.join(save_root_path, 'Tick', date)
    else:
        save_path = os.path.join(save_root_path, dtype, date)
#    df.to_pickle(os.path.join(save_path, '%s.pkl' % stock), compression = 'gzip')
    return (stock,df)

def diller(file_name, payload=None):
    if payload is None:
        with open(file_name, 'rb') as fin:
            return dill.load(fin)
    else:
        with open(file_name, 'wb') as fout:
            dill.dump(payload, fout, protocol=4)
            
def retrieve_by_date(date, save_root_path = '/arch1/group/800466/warehouse/prod/MD/CHINA_STOCK/'):
    print(date, ' start retrieve')
    last_tday = udt.get_trading_day_offset(date,-1)[0].strftime('%Y%m%d')
    iw = IO.read_data([last_tday],columns=['index_weight_hs300','index_weight_zz500'], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    iw = iw[(iw.index_weight_zz500 > 0) | (iw.index_weight_hs300 > 0)]
    stock_list = iw.index.get_level_values(1).tolist()
    for dty in ['Transaction', 'Order', 'Stock']:
        para_list = [[x,str(date),dty] for x in stock_list]
        if dty == 'Stock':
            save_path = os.path.join(save_root_path, 'Tick', str(date))
        else:
            save_path = os.path.join(save_root_path, dty, str(date))
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        with Pool(24) as pool:
            pool.map(get_level2_data, para_list)
        
    print(date, ' finished')
    
def retrieve_stopping_by_date(date, save_root_path = '/arch0/group/800466/warehouse/prod/MD/20230222_starts688/'):
    print(date, ' start retrieve')
    stock_list = IO.read_data([20230217], columns = ['close']).index.get_level_values(1).tolist()
    stock_list = [x for x in stock_list if x.startswith('688')]
    for dty in ['Stock','Transaction', 'Order']:
        print(dty)
        para_list = [[x,str(date),dty] for x in stock_list]
        
        if dty == 'Stock':
            save_path = os.path.join(save_root_path, 'Tick')
        else:
            save_path = os.path.join(save_root_path, dty)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        with Pool(24) as pool:
            rlist = pool.map(get_level2_data, para_list)
        diller(os.path.join(save_path, '%s.pkl' % str(date)), dict(rlist))
    print(date, ' finished')
    
sdate,edate,cdate_list = check_update_date()
for date in cdate_list:
    retrieve_stopping_by_date(date)