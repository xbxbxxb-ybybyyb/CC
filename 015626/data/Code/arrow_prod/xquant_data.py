import pandas as pd
import numpy as np
import datetime
import re
import os
import warnings
from xquant.marketdata import MarketData as XMD
from xquant.thirdpartydata.marketdata import MarketData as XMDTP
import multifactor.utility.common as ut
import concurrent.futures


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
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))


def get_level2_data(para, save_path, dtype, append_cancel_orders=False, force_override=False):
    assert len(para) == 2 and isinstance(para[0], str) and isinstance(para[1], str)
    stock = para[0]
    date = para[1]
    assert dtype in ['Transaction', 'Order', 'Stock', 'Order_RAW']
    csv_path = os.path.join(save_path, dtype, stock, date + '.csv')
    if os.path.exists(csv_path) and not force_override:
        if dtype == 'Stock':
            print(f'{stock} {dtype} data already exists at {date}')
            return
        else:
            # detect ApplSeqNum existence
            data = pd.read_csv(csv_path, nrows=0)
            if 'ApplSeqNum' in data.columns:
                print(f'{stock} {dtype} data already exists at {date}')
                return
            else:
                print(f'{stock} {dtype} data missing ApplSeqNum, overridden at {date}')

    try:
        md = XMD()
        mdtp = XMDTP()

        if dtype == 'Order' or dtype =='Order_RAW':
            if dtype == 'Order' and '.SH' in stock:
                df_transaction = mdtp.getMDTransactionDataFrame(stock, date + '000000', date + '235959')
                df_order = mdtp.getMDOrderDataFrame(stock, date + '000000', date + '235959')
                df = reform_sh_order(df_order, df_transaction, append_cancel_orders=append_cancel_orders)
            else:
                df = mdtp.getMDOrderDataFrame(stock, date + '000000', date + '235959')
        elif dtype == 'Transaction':
            df = mdtp.getMDTransactionDataFrame(stock, date + '000000', date + '235959')
        elif dtype == 'Stock':
            # df = md.get_data_by_date("Stock", stock, str(date))
            df = mdtp.getMDSecurityTickDataFrame(stock, date + '000000', date + '235959', 1)
        else:
            raise NotImplementedError

        del(md)
        del(mdtp)
    except:
        df = pd.DataFrame()

    if len(df) == 0:
        warnings.warn(f'{stock} {dtype} data does not exist at {date}')
        return

    df['dt'] = df.apply(lambda x: format_datetime(x.MDDate, x.MDTime), axis=1)
    # for Order
    if dtype == 'Order':
        droplist = ['MDDate', 'MDTime', 'HTSCSecurityID']
    elif dtype == 'Transaction':
        droplist = ['MDDate', 'MDTime', 'SecurityType', 'HTSCSecurityID']
    # elif dtype == 'Stock':
    #     droplist = ['MDDate', 'MDTime', 'SecurityType', 'HTSCSecurityID', 'ReceiveDateTime', 'MDRecordID', 'MDReportID', 'MDStreamID', 'SecuritySubType',
    #                 'SecurityIDSource', 'Symbol', 'MDLevel', 'MDChannel', 'TradingPhaseCode', 'SwitchStatus', 'MDRecordType', 'MDValidType']
    elif dtype == 'Stock':
        droplist = ['MDDate', 'MDTime', 'SecurityType', 'HTSCSecurityID', 'ReceiveDateTime']
    else:
        droplist = []
    df = df.drop(droplist, axis=1)

    if not os.path.exists(os.path.dirname(csv_path)):
        os.makedirs(os.path.dirname(csv_path))
    df.set_index('dt').to_csv(csv_path)
    print(f'{stock} {dtype} data at {date} dumped successfully')


def retrieve_level2_by_h5(h5_path, save_path, dtype, max_workers, **kwargs):
    if isinstance(h5_path, str):
        df = pd.read_hdf(h5_path)
    else:
        assert isinstance(h5_path, pd.DataFrame) or isinstance(h5_path, pd.Series)
        df = h5_path
    assert isinstance(df.index, pd.MultiIndex) and df.index.names == ['dt', 'Ticker']
    df = df.reset_index()
    df['dt'] = df['dt'].dt.strftime('%Y%m%d')
    para_list = df[['Ticker','dt']].values.tolist()
    ut.concurrent_apply_func(get_level2_data, para_list, max_workers, process_type='multiprocess',
                             debug_mode=False, collect_results=False,
                             save_path=save_path, dtype=dtype, **kwargs)

