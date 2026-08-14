# -*- coding: utf-8 -*-
from xquant.factordata import FactorData
import pandas as pd
import os
from multiprocessing import Pool


def maxOrderNo(df):
    if df["TradeBuyNo"] > df["TradeSellNo"]:
        return df["TradeBuyNo"]
    else:
        return df["TradeSellNo"]


def maxOrderSide(df):
    if df["TradeBuyNo"] > df["TradeSellNo"]:
        return 1
    else:
        return 2


def getprice(df):
    if df["OrderBSFlag"] == 1:
        return df["OrderPriceMax"]
    else:
        return df["OrderPriceMin"]


def get_sh_order(update_date, stock):
    from xquant.thirdpartydata.marketdata import MarketData
    ma = MarketData()
    update_date=str(update_date)
    print(update_date, stock)
    try:
        starttime = update_date + "090000"
        endtime = update_date + "160000"
        orders = ma.getMDOrderDataFrame(stock, starttime, endtime)
        orders = orders.drop_duplicates(subset=['ApplSeqNum'], keep='first')
        trades = ma.getMDTransactionDataFrame(stock, starttime, endtime)
        trades = trades.drop_duplicates(subset=['ApplSeqNum'], keep='first')

        orders = orders[orders["OrderType"] != 10]
        trades = trades[trades["TradeType"] == 0]

        trades = trades[trades["MDTime"] >= "093000000"]
        trades = trades[trades["MDTime"] <= "145700000"]

        trades["OrderNO"] = trades.apply(maxOrderNo, axis=1)
        trades["OrderBSFlag"] = trades.apply(maxOrderSide, axis=1)

        simple_trades = trades[["MDDate", "MDTime", "OrderNO", "TradePrice", "TradeQty", "OrderBSFlag"]]
        simple_trades.columns = ["MDDate", "MDTime", "OrderNO", "OrderPrice", "OrderQty", "OrderBSFlag"]
        simple_trades["type"] = "Trade"

        simple_orders = orders[["MDDate", "MDTime", "OrderNO", "OrderPrice", "OrderQty", "OrderBSFlag","OrderType"]]
        simple_orders["type"] = "Order"

        new_df = pd.concat([simple_trades, simple_orders])

        agg_dict = {"MDDate": ['min'], 'MDTime': ['min'], "OrderPrice": ['min', 'max'], 'OrderQty': ['sum'],
                    "OrderBSFlag": ["min"],"OrderType":["min"]}
        df = new_df.groupby("OrderNO").agg(agg_dict)
        df = df.reset_index()
        df.columns = ['OrderNo', 'MDDate', 'MDTime', 'OrderPriceMin', 'OrderPriceMax', 'OrderQty', 'OrderBSFlag',"OrderType"]
        df["OrderPrice"] = df.apply(getprice, axis=1)
        df = df[['OrderNo', 'MDDate', 'MDTime', 'OrderPrice', 'OrderQty', 'OrderBSFlag',"OrderType"]]
        # print(df)
    except Exception as e:
        df = pd.DataFrame()
        print(e, stock, update_date)
    return df
    #filepath = result_path+"%s/%s_%s_orders.pkl"%(update_date, update_date, stock)
    #df.to_pickle(filepath)



