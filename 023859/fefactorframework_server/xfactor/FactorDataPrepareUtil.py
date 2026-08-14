import time
import decimal
import pandas as pd
from loguru import logger
import numpy as np
import datetime as dt

def find_repeat_tick(tick_data, repeat_filter_cols):
    tick_data['inf_str'] = tick_data[repeat_filter_cols].apply(lambda x: str(x.values), axis=1)
    tick_data['last_inf_str'] = tick_data['inf_str'].shift(1)
    return tick_data['inf_str'] == tick_data['last_inf_str']

# convert xdb order df to designated format
def prepare_order_data_new(df, base_date):
    try:
        # st = time.time()
        df.columns = ['symbol', 'appl_seq_num', 'OrderIndex', 'OrderPrice', 'OrderQty', "MDTime", "order_index",
                      'local_index', "OrderBSFlag", "OrderType", "MDDate", "timestamp",
                     'ff_shares', 'pre_close', 'industry',
                     'after_not_ul_len', 'HTSCSecurityID', 'Ticker', 'pattern', 'dt']
        df["dt"] = pd.to_datetime(df["dt"])
        df['OrderBSFlag'] = df['OrderBSFlag'].apply(lambda x: int(x))
        df['OrderType'].replace('U','3',inplace = True) # xdb接口用U表示本方最优，转换为int类型的3，从而和xquant一致
        df['OrderType'] = df['OrderType'].apply(lambda x : int(x))
        df.set_index(["dt", "Ticker"], inplace=True)
        df = df[['MDDate', 'MDTime', 'OrderIndex', 'OrderPrice', 'OrderQty', 'OrderBSFlag', "OrderType",
                 'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close']]
        for col in ['OrderPrice','pre_close']:
            df[col] = df[col].apply(lambda x : round_(x,2))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x : round_(x,4))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x : int(round_(x,0)))
    except Exception as e:
        logger.error(
            "Order数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df



# convert xdb trade df to designated format
def prepare_trade_data_new(df, base_date):
    try:
        # st = time.time()
        df.columns = ['symbol', 'appl_seq_num', 'TradeBuyNo', 'TradeSellNo', 'TradePrice', "TradeQty", "MDTime", "TradeIndex",
                      'local_index', "TradeBSFlag", "MDDate", "timestamp",
                     'ff_shares', 'pre_close', 'industry', 'after_not_ul_len', 'HTSCSecurityID', 'Ticker', 'pattern', 'dt']
        # ed = time.time()
        # logger.info("rename cost={}".format(ed - st))
        # st = time.time()
        df["TradeMoney"] = (df["TradeQty"] * df["TradePrice"]).apply(lambda x : round_(x,2))
        df["TradeType"] = 0
        df['TradeBSFlag'] = df['TradeBSFlag'].apply(lambda x: int(x))
        df["dt"] = pd.to_datetime(df["dt"])
        df.set_index(["dt", "Ticker"], inplace=True)
        df = df[['MDDate', 'MDTime',
                 'TradeIndex', 'TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty',
                 'TradeMoney', 'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close']]
        for col in ['TradePrice','pre_close']:
            df[col] = df[col].apply(lambda x : round_(x,2))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x : round_(x,4))
        # for col in ['industry','after_not_ul_len']:
        #     df[col] = df[col].apply(lambda x : round_(x,1))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x : int(round_(x,0)))

    except Exception as e:
        logger.error(
            "Trade数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df

def prepare_tickaddorder_data_new(df, base_date):
    try:
        # st = time.time()
        df.columns = ['symbol', "MDDate", "MDTime", "timestamp", "appl_seq_num",
                      "OpenPx", "LastPx", "HighPx", "LowPx", "TotalOfferQty", "TotalBidQty",
                      "WeightedAvgOfferPx", "WeightedAvgBidPx", "TotalVolumeTrade", 'TotalValueTrade', 'VolumeTrade',
                      "NumTrades", 'TradingPhaseCode', 'last_local_index',
                      "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price",
                      "Sell6Price", "Sell7Price", "Sell8Price", "Sell9Price", "Sell10Price",
                      "Sell1OrderQty", "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
                      "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty", "Sell10OrderQty",
                      "Sell1NumOrders", "Sell2NumOrders", "Sell3NumOrders", "Sell4NumOrders", "Sell5NumOrders",
                      "Sell6NumOrders", "Sell7NumOrders", "Sell8NumOrders", "Sell9NumOrders", "Sell10NumOrders",

                      "Buy1Price", "Buy2Price", "Buy3Price", "Buy4Price", "Buy5Price",
                      "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price", "Buy10Price",
                      "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty", "Buy5OrderQty",
                      "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
                      "Buy1NumOrders", "Buy2NumOrders", "Buy3NumOrders", "Buy4NumOrders", "Buy5NumOrders",
                      "Buy6NumOrders", "Buy7NumOrders", "Buy8NumOrders", "Buy9NumOrders", "Buy10NumOrders",
                      'OrderType', 'OrderPrice', 'OrderQty',
                      'ff_shares', 'pre_close', 'industry',
                      'after_not_ul_len', 'HTSCSecurityID', 'Ticker', 'pattern', 'dt']

        df["dt"] = pd.to_datetime(df["dt"])
        df.set_index(["dt", "Ticker"], inplace=True)
        df["OrderPrice"].fillna(-1.0, inplace=True)
        df["OrderQty"].fillna(-1.0, inplace=True)
        df['VolumeTrade'] = df.groupby(["dt", "Ticker"])['TotalVolumeTrade'].diff().fillna(df['TotalVolumeTrade'])

        df = df[[
            "MDDate", "MDTime", "NumTrades", "TotalVolumeTrade", "TotalValueTrade", "VolumeTrade", "LastPx",
            'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close', "OpenPx", "HighPx", "LowPx",
            "TotalBidQty",
            "TotalOfferQty", "WeightedAvgBidPx", "WeightedAvgOfferPx", "Buy1Price", "Buy2Price",
            "Buy3Price", "Buy4Price", "Buy5Price", "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price",
            "Buy10Price", "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty", "Buy5OrderQty",
            "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
            "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price", "Sell6Price", "Sell7Price",
            "Sell8Price", "Sell9Price", "Sell10Price", "Sell1OrderQty",
            "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
            "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty",
            "Sell10OrderQty",
            'appl_seq_num', 'OrderType', 'OrderPrice', 'OrderQty']]
        for col in ['pre_close', 'VolumeTrade']:
            df[col] = df[col].apply(lambda x: round_(x, 2))
        for col in ['WeightedAvgBidPx', 'WeightedAvgOfferPx']:
            df[col] = df[col].apply(lambda x: round_(x, 3))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x: round_(x, 4))
        # for col in ['industry','after_not_ul_len']:
        #     df[col] = df[col].apply(lambda x : round_(x,1))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x: int(round_(x, 0)))

    except Exception as e:
        logger.error(
            "EnTick数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df



# 将XDB返回的tick数据清洗成金工统一格式
# @param df : xdb取出的单标的tick数据
# @param base_date : 数据窗口结束日期 (例如从20230928起回看5天，则这五天所有数据的base_date都是20230928)
def prepare_tick_data_new(df, base_date, tick_type):
    try:
        # st = time.time()
        df.columns = ['symbol', "MDDate", "MDTime", "timestamp",
                     "OpenPx", "LastPx", "high_px", "low_px", "TotalOfferQty", "TotalBidQty",
                     "WeightedAvgOfferPx", "WeightedAvgBidPx", "TotalVolumeTrade", 'TotalValueTrade', 'VolumeTrade',
                     "NumTrades", 'TradingPhaseCode',
                     "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price",
                     "Sell6Price", "Sell7Price", "Sell8Price", "Sell9Price", "Sell10Price",
                     "Sell1OrderQty","Sell2OrderQty","Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
                     "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty", "Sell10OrderQty",
                     "Sell1NumOrders", "Sell2NumOrders", "Sell3NumOrders", "Sell4NumOrders", "Sell5NumOrders",
                     "Sell6NumOrders", "Sell7NumOrders", "Sell8NumOrders", "Sell9NumOrders", "Sell10NumOrders",

                     "Buy1Price", "Buy2Price","Buy3Price", "Buy4Price", "Buy5Price",
                     "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price", "Buy10Price",
                     "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty","Buy5OrderQty",
                     "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
                     "Buy1NumOrders", "Buy2NumOrders", "Buy3NumOrders", "Buy4NumOrders", "Buy5NumOrders",
                     "Buy6NumOrders", "Buy7NumOrders", "Buy8NumOrders", "Buy9NumOrders", "Buy10NumOrders",
                     'ff_shares', 'pre_close', 'industry',
                     'after_not_ul_len', 'HTSCSecurityID', 'Ticker', 'pattern', 'dt']

        df["dt"] = pd.to_datetime(df["dt"])
        if tick_type in ['xdb_tickex', 'xdb_tickex_cs']:  # 对tickex执行去重，915筛选
            repeat_filter_cols = ['dt','Ticker','NumTrades', 'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'TotalBidQty',
                                  'TotalOfferQty',
                                  'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TradingPhaseCode'] + \
                                 ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Sell%dPrice' % (i) for i in
                                                                               range(1, 11)] + \
                                 ['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i
                                                                                  in
                                                                                  range(1, 11)]
            df['repeat_filter'] = find_repeat_tick(df.copy(), repeat_filter_cols)
            df = df[~df['repeat_filter']]
            df = df[df['MDTime'] >= 91500000]
        df.set_index(["dt", "Ticker"], inplace=True)

        df = df[[
            "MDDate", "MDTime", "NumTrades", "TotalVolumeTrade", "TotalValueTrade", "VolumeTrade", "LastPx",
            'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close', "OpenPx",
            "TotalBidQty",
            "TotalOfferQty", "WeightedAvgBidPx", "WeightedAvgOfferPx", "Buy1Price", "Buy2Price",
            "Buy3Price", "Buy4Price", "Buy5Price", "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price",
            "Buy10Price", "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty","Buy5OrderQty",
            "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
            "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price", "Sell6Price", "Sell7Price",
            "Sell8Price", "Sell9Price", "Sell10Price", "Sell1OrderQty",
            "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
            "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty",
            "Sell10OrderQty"]]
        for col in ['WeightedAvgBidPx','WeightedAvgOfferPx','pre_close']:
            df[col] = df[col].apply(lambda x : round_(x,2))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x : round_(x,4))
        # for col in ['industry','after_not_ul_len']:
        #     df[col] = df[col].apply(lambda x : round_(x,1))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x : int(round_(x,0)))

    except Exception as e:
        logger.error(
            "Tick数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df

# ====================================================================================================================
# 以下为因子开发时的公共函数

def cal_time_delta(start, end):
    start_str = str(int(start))
    end_str = str(int(end))
    time_delta = (int(end_str[:~6]) - int(start_str[:~6])) * 3600000 + \
                 (int(end_str[~6:~4]) - int(start_str[~6:~4])) * 60000 + \
                 (int(end_str[~4:~2]) - int(start_str[~4:~2])) * 1000 + \
                 (int(end_str[~2:]) - int(start_str[~2:]))
    if (start < 120000000) & (end > 120000000):
        time_delta = time_delta - 5400000
    return time_delta


def cal_ul_price(pre_close_dataframe):
    pre_close_dataframe = pre_close_dataframe.reset_index()
    after_824 = pre_close_dataframe['dt'] >= pd.Timestamp('20200824')
    cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2] == '30')
    kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2] == '68')
    pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.1 + 0.5) / 100
    pre_close_dataframe.loc[(after_824 & cyb) | kcb, 'ul_price'] = np.floor(
        pre_close_dataframe['pre_close'] * 100 * 1.2 + 0.5) / 100
    return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']

# 浮点数处理
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res


def filter_930(df):
    return df[df["MDTime"] >= 93000000]


def get_time_delta(itime):
    mls = int(str(int(itime))[-3:])
    s = int(str(int(itime))[-5:-3])
    m = int(str(int(itime))[-7:-5])
    h = int(str(int(itime))[:-7])
    time_mls = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + mls
    time_mls_900 = 9 * 3600 * 1000
    if int(itime) > 120000000:
        time_delta = time_mls - time_mls_900 - 5400000
    else:
        time_delta = time_mls - time_mls_900
    return time_delta


# 生成距离9点的毫秒数
# @param df : 原始数据
# @param name : 生成数据的列名，不写默认为"MDTime_delta"
def generate_time_delta_930(df, name=""):
    name = "MDTime_delta" if name == "" else name
    df[name] = df['MDTime'].apply(lambda x: get_time_delta(x))
    return df


# 生成成交额
# @param df : 原始数据
# @param name : 生成数据的列名，不写默认为"OrderAmt"
def generate_order_amount(df, name=""):
    name = "OrderAmt" if name == "" else name
    df[name] = df['OrderPrice'] * df['OrderQty']
    return df


# 剔除价格和成交额为0的数据
# @param df : 原始数据
def filter_transaction(df):
    df = df[(df['TradePrice'] > 0) & (df['TradeMoney'] > 0)]
    return df


# 生成tick成交额
# @param df : 原始数据
# @param name : 生成数据的列名，不写默认为"ValueTrade"
def generate_tick_trade_value(df, name=""):
    name = "ValueTrade" if name == "" else name
    df[name] = df['TotalValueTrade'] - df['TotalValueTrade'].shift(1).fillna(0)
    return df


# 生成tick成交量
# @param df : 原始数据
# @param name : 生成数据的列名，不写默认为"VolumeTrade"
def generate_tick_trade_volume(df, name=""):
    name = "VolumeTrade" if name == "" else name
    df[name] = df['TotalVolumeTrade'] - df['TotalVolumeTrade'].shift(1).fillna(0)
    return df

#计算给定时间戳time1在sec_delta秒后的时间戳
def fun_get_time(time1,sec_delta):
    tmp_time = dt.datetime.strptime(str(time1)[:-3],'%H%M%S')
    tmp_time2 = tmp_time+dt.timedelta(seconds=sec_delta)
    tmp_time2_str = tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
    if (int(tmp_time2_str)>113000000)&(time1<=113000000):
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=1.5*3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str)<130000000)&(time1>=130000000):
        adj_tmp_time2 = tmp_time2-dt.timedelta(seconds=1.5*3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str)<93000000)&(time1>=93000000):
        adj_tmp_time2_str = '92500000'
        return int(adj_tmp_time2_str)
    elif (time1<93000000):
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=4*60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)
#注册制处理
def fun_zcz_tick(data_df,price_names = ['HighPx', 'LowPx','LastPx',  'WeightedAvgBidPx', 'WeightedAvgOfferPx',
                   'Buy1Price', 'Buy2Price', 'Buy3Price', 'Buy4Price', 'Buy5Price', 'Buy6Price', 'Buy7Price',
                   'Buy8Price', 'Buy9Price', 'Buy10Price', 'Sell1Price', 'Sell2Price', 'Sell3Price', 'Sell4Price',
                   'Sell5Price', 'Sell6Price', 'Sell7Price', 'Sell8Price', 'Sell9Price', 'Sell10Price']):
    dt, ticker = data_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = data_df['pre_close'].values[0]
    if zcz:
        data_df[price_names] = ((data_df[price_names] / pre_close - 1) / 2 + 1) * pre_close
    return data_df

# 财务-获取报告期对应的X季报类别
def get_report_period(x):
    month = x[4:6]
    if month == '03':
        return 1
    elif month == '06':
        return 2
    elif month == '09':
        return 3
    elif month == '12':
        return 4
    else:
        return 5