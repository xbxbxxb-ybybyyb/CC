# insight imports
from insight.model import MarketData_pb2 as MarketData_pb2
from insight.model import InsightErrorContext_pb2 as InsightErrorContext_pb2
from insight.model import EMarketDataType_pb2 as EMarketDataType
from insight.model import MDQuery_pb2 as MDQuery_pb2
from insight.model import ESecurityIDSource_pb2 as ESecurityIDSource
from insight.model import ESecurityType_pb2 as ESecurityType
from insight.model import MDSubscribe_pb2 as MDSubscribe_pb2
from insight.model import MDPlayback_pb2 as MDPlayback_pb2
from insight.interface import mdc_gateway_interface as mdc_gateway_interface
from insight.data_handle import OnRecvMarkertDataBase
from insight import utils
# misc
import inspect
from collections import Iterable
import pandas as pd
import numpy as np
import os


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


def login(user_id):
    # 流量与日志开关设置
    # open_trace trace流量日志开关 # params:open_file_log 本地日志文件开关  # params:open_cout_log 控制台日志开关
    open_trace = True
    open_file_log = True
    open_cout_log = False
    utils.get_interface().init(open_trace, open_file_log, open_cout_log)

    # 接管日志
    # 若想关闭系统日志,自我处理日志,打开本方法
    # 打开本方法后,日志在insightlog.py的PyLog类的方法log(self,line)中也会体现,其中 line为日志内容）
    # use_init = True 系统日志以 utils.get_interface().init 配置的方式记录
    # use_init = False 系统不再记录或打印任何日志,日志只有自行处理部分处理
    ### 以下是示例 ###
    # use_init = True
    # utils.get_interface().own_deal_log(use_init)
    utils.login(user_id)


def set_interface_callback(callback_instance):
    utils.get_interface().setCallBack(callback_instance)


def logout():
    utils.fini()


class OnRecvMarkertData(OnRecvMarkertDataBase):
    def __init__(self, valid_cols):
        self.collector = dict()
        assert isinstance(valid_cols, Iterable)
        self.valid_cols = valid_cols

    def OnMarketData(self, marketdata: MarketData_pb2.MarketData):
        ##处理订阅的实时行情数据
        try:
            if marketdata.marketDataType == EMarketDataType.MD_TICK:  # .MD_TICK 快照
                if marketdata.HasField("mdStock"):  # 股票
                    print("HTSCSecurityID=%s MDTime=%s" % (marketdata.mdStock.HTSCSecurityID, marketdata.mdStock.MDTime))
                elif marketdata.HasField("mdIndex"):  # 指数
                    print("HTSCSecurityID=%s lastprice=%d" % (marketdata.mdIndex.HTSCSecurityID, marketdata.mdIndex.LastPx))
                elif marketdata.HasField("mdBond"):  # 债券
                    print("HTSCSecurityID=%s lastprice=%d" % (marketdata.mdBond.HTSCSecurityID, marketdata.mdBond.LastPx))
                elif marketdata.HasField("mdFund"):  # 基金
                    print("HTSCSecurityID=%s lastprice=%d" % (marketdata.mdFund.HTSCSecurityID, marketdata.mdFund.LastPx))
                elif marketdata.HasField("mdOption"):  # 期权
                    print("HTSCSecurityID=%s lastprice=%d" % (marketdata.mdOption.HTSCSecurityID, marketdata.mdOption.LastPx))
            elif marketdata.marketDataType == EMarketDataType.MD_TRANSACTION:  # .MD_TRANSACTION:逐笔成交
                if marketdata.HasField("mdTransaction"):
                    print(marketdata.mdTransaction)
            elif marketdata.marketDataType == EMarketDataType.MD_ORDER:  # .MD_ORDER:逐笔委托
                if marketdata.HasField("mdOrder"):
                    print(marketdata.mdOrder)
            elif marketdata.marketDataType == EMarketDataType.MD_CONSTANT:  # .MD_CONSTANT:静态信息
                if marketdata.HasField("mdConstant"):
                    print(marketdata.mdConstant.HTSCSecurityID)
                # MD_KLINE:实时数据只提供15S和1MIN K线
            elif marketdata.marketDataType == EMarketDataType.MD_KLINE_15S or \
                 marketdata.marketDataType == EMarketDataType.MD_KLINE_1MIN or \
                 marketdata.marketDataType == EMarketDataType.MD_KLINE_5MIN or \
                 marketdata.marketDataType == EMarketDataType.MD_KLINE_15MIN or \
                 marketdata.marketDataType == EMarketDataType.MD_KLINE_30MIN or \
                 marketdata.marketDataType == EMarketDataType.MD_KLINE_60MIN or \
                 marketdata.marketDataType == EMarketDataType.MD_KLINE_1D:
                if marketdata.HasField("mdKLine"):
                    print(marketdata.mdKLine)
            elif marketdata.marketDataType == EMarketDataType.MD_TWAP_1S or marketdata.marketDataType == EMarketDataType.MD_TWAP_1MIN:  # .TWAP:TWAP数据
                if marketdata.HasField("mdTwap"):
                    print(marketdata.mdTwap)
            elif marketdata.marketDataType == EMarketDataType.MD_VWAP_1S or marketdata.marketDataType == EMarketDataType.MD_VWAP_1MIN:  # .VWAP:VWAP数据
                if marketdata.HasField("mdVwap"):
                    print(marketdata.mdVwap)
            elif marketdata.marketDataType == EMarketDataType.AD_FUND_FLOW_ANALYSIS:  # .AD_FUND_FLOW_ANALYSIS:
                if marketdata.HasField("mdFundFlowAnalysis"):
                    print(marketdata.mdFundFlowAnalysis)
            elif marketdata.marketDataType == EMarketDataType.MD_ETF_BASICINFO:  # .MD_ETF_BASICINFO:ETF成分股信息
                if marketdata.HasField("mdETFBasicInfo"):
                    print(marketdata.mdETFBasicInfo)
        except BaseException as e:
            print("onMarketData error happended!")
            print(e)

    def OnPlaybackPayload(self, playload: MDPlayback_pb2.PlaybackPayload):
        # 处理订阅的回放行情数据
        try:
            utils.interface.set_service_value(4)
            print("Parse Message id:" + playload.taskId)
            marketDataStream = playload.marketDataStream;
            print("OnPlaybackPayload total number=%d, serial=%d, isfinish=%d" % (
                   marketDataStream.totalNumber, marketDataStream.serial,
                   marketDataStream.isFinished));
            marketDataList = marketDataStream.marketDataList
            marketDatas = marketDataList.marketDatas
            for data in marketDatas:
                self.OnMarketData(data)
        except BaseException as e:
            print(e)

    def OnPlaybackStatus(self, status:MDPlayback_pb2.PlaybackStatus):
        try:
            print("OnPlaybackStatus playback status=%d" %(status.taskStatus))
            utils.interface.set_service_value(status.taskStatus)
            if(status.taskStatus == MDPlayback_pb2.CANCELED or status.taskStatus == MDPlayback_pb2.COMPLETED or status.taskStatus == MDPlayback_pb2.FAILED):
                utils.interface.mutex.acquire()
                if status.taskId in utils.interface.task_id_status:
                    del utils.interface.task_id_status[status.taskId]
                utils.interface.mutex.release()
        except BaseException as e:
            print("error happended in OnPlaybackStatus")
            print(e)

    def OnPlaybackResponse(self,response:MDPlayback_pb2.PlaybackResponse):
        try:
            if response.isSuccess:
                print("OnPlaybackResponse Message id:" + response.taskId)
            else:
                #print(response.errorContext.errorCode)
                print("OnPlaybackResponse failed --> %s" %(response.errorContext.message))
        except BaseException as e:
            print("error happended in OnPlaybackResponse")
            print(e)

    def OnPlaybackControlResponse(self, response:MDPlayback_pb2.PlaybackControlResponse):
        try:
            if response.isSuccess:
                print(response.currentReplayRate)
                print("OnPlaybackControlResponse Message id:" + response.taskId)
            else:
                print("OnPlaybackControlResponse failed!!! reason -> %s" %(response.errorContext.message))
        except BaseException as e:
            print("error happended in OnPlaybackControlResponse")
            print(e)

    def OnServiceMessage(self, marketDataStream:MarketData_pb2.MarketDataStream):
        try:
            utils.interface.set_service_value(1)
        except BaseException as e:
            print("error happended in OnServiceMessage")
            print(e)

    def OnSubscribeResponse(self, response:MDSubscribe_pb2.MDSubscribeResponse):
        try:
            if response.isSuccess:
                print("Subscribe Success!!!")
            else:
                #print(gateway.getErrorCodeValue(response.errorContext.errorCode))
                print("Subscribe failed!!! reason ->%s" %(response.errorContext.message))
        except BaseException as e:
            print("error happended in OnServiceMessage")
            print(e)

    def OnQueryResponse(self, response:MDQuery_pb2.MDQueryResponse):
        try:
            if response.isSuccess:
                marketDataStream = response.marketDataStream;
                print(
                    "query response total number=%d, serial=%d, isfinish=%d" % (marketDataStream.totalNumber, marketDataStream.serial,
                                                                 marketDataStream.isFinished));
                marketDataList = marketDataStream.marketDataList
                marketDatas = marketDataList.marketDatas
                for data in marketDatas:
                    self.OnMarketData(data)
                utils.interface.set_query_exit(marketDataStream.isFinished == 1)
            else:
                print("OnQueryResponse failed!!! reason -> %s" %(response.errorContext.message))
                utils.interface.set_query_exit(True)
        except BaseException as e:
            print("error happended in OnQueryResponse")
            print(e)

    def OnGeneralError(self, context:InsightErrorContext_pb2.InsightErrorContext):
        try:
            #print(gateway.getErrorCodeValue(context.errorCode))
            print("OnGeneralError!!! reason -> %s" % (context.message))
        except BaseException as e:
            print("error happended in OnGeneralError")
            print(e)

    def OnLoginSuccess(self):
        print("OnLoginSuccess!!!")

    def OnLoginFailed(self, error_no, message):
        try:
            print("OnLoginFailed!!! reason -> %s" %message)
        except BaseException as e:
            print("error happended in OnLoginFailed")
            print(e)

    def OnNoConnections(self):
        print("OnNoConnections!!!")
        utils.interface.set_reconnect(True)
        utils.interface.set_no_connections(True)

    def OnReconnect(self):
        print("OnReconnect!!!")
        utils.interface.set_reconnect(True)
        utils.interface.set_reconnect_count(utils.interface.get_reconnect_count() + 1)


@static_vars(run_once=False)
def job_wrapper(func_call, callback_class, postprocess_func=None, requested_cols=None,
                user_id='015626', output_path=None, release_resource=False, **kwargs):
    assert callable(func_call)
    assert inspect.isclass(callback_class) and issubclass(callback_class, OnRecvMarkertData)
    assert requested_cols is None or isinstance(requested_cols, Iterable)
    instance = callback_class()
    if not job_wrapper.run_once:
        login(user_id)
        job_wrapper.run_once = True
    set_interface_callback(instance)
    func_call(**kwargs)
    if requested_cols is None:
        valid_cols = instance.valid_cols
    else:
        valid_cols = requested_cols
    data = {k: {col: getattr(v, col) for col in valid_cols if hasattr(v, col)} for k, v in instance.collector.items()}
    data_pd = pd.DataFrame(data.values()).infer_objects()
    if postprocess_func is not None:
        assert callable(postprocess_func)
        data_pd = postprocess_func(data_pd)
    if release_resource:
        logout()
        job_wrapper.run_once = False
    if output_path is not None:
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        data_pd.to_hdf(output_path, 'insight', mode='w')
    return data_pd


class OnRecvMDConstant(OnRecvMarkertData):
    def __init__(self):
        valid_cols = ['HTSCSecurityID', 'ListDate', 'OutstandingShare', 'PublicFloatShareQuantity', 'MDDate', 'PreClosePx',
                      'MaxPx', 'MinPx', 'BuyQtyUnit']
        super(OnRecvMDConstant, self).__init__(valid_cols)

    def OnMarketData(self, marketdata: MarketData_pb2.MarketData):
        try:
            if marketdata.marketDataType == EMarketDataType.MD_CONSTANT:
                if marketdata.HasField("mdConstant"):
                    self.collector[marketdata.mdConstant.HTSCSecurityID] = marketdata.mdConstant
        except BaseException as e:
            print("onMarketData error happended!")
            print(e)


# 查询今日最新的指定证券的基础信息 -- 在data_handle.py 数据回调接口OnMarketData()中marketdata.marketDataType = MD_CONSTANT
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
def query_last_mdcontant(security_type=ESecurityType.StockType):
    if security_type == ESecurityType.StockType:
        # 按市场查询
        # 沪市 股票
        security_idsource0= ESecurityIDSource.XSHG
        idsource_and_type0 = mdc_gateway_interface.SecurityIDSourceAndType(security_idsource0, security_type)
        # 深市 股票
        security_idsource1 = ESecurityIDSource.XSHE
        idsource_and_type1 = mdc_gateway_interface.SecurityIDSourceAndType(security_idsource1, security_type)
        # security_idsource_and_types 与 security_id_list 并集
        security_idsource_and_types = [idsource_and_type0, idsource_and_type1]
    # 按标的查询
    # params:security_id_list 为 标的集合
    security_id_list = []  # 置空表示不额外查询某些标的
    ######## 市场和标的 并集关系，如果不需要其中某项，请将数组置空
    utils.get_interface().queryLastMdContantCallback(security_idsource_and_types, security_id_list)


def postprocess_mdconstant(data_pd):
    data_pd = data_pd.reset_index(drop=True)
    data_pd = data_pd.set_index(['HTSCSecurityID']).sort_index()
    data_pd.index.name = 'Ticker'
    return data_pd


class OnRecvFuturesTick(OnRecvMarkertData):
    def __init__(self):
        valid_cols = ['HTSCSecurityID', 'MDDate', 'MDTime', 'MaxPx', 'MinPx', 'PreClosePx', 'NumTrades',
                      'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx',
                      'TradingDate', 'PreOpenInterest', 'PreSettlePrice', 'OpenInterest', 'SettlePrice',
                      'BuyPriceQueue', 'BuyOrderQtyQueue', 'SellPriceQueue', 'SellOrderQtyQueue', 'BuyOrderQueue',
                      'SellOrderQueue', 'BuyNumOrdersQueue', 'SellNumOrdersQueue']
        super(OnRecvFuturesTick, self).__init__(valid_cols)

    def OnMarketData(self, marketdata: MarketData_pb2.MarketData):
        try:
            if marketdata.marketDataType == EMarketDataType.MD_TICK:
                if marketdata.HasField("mdFuture"):
                    self.collector[(marketdata.mdFuture.HTSCSecurityID,
                                    marketdata.mdFuture.MDDate,
                                    marketdata.mdFuture.MDTime)] = marketdata.mdFuture
        except BaseException as e:
            print("onMarketData error happended!")
            print(e)


class OnRecvStockTick(OnRecvMarkertData):
    def __init__(self):
        valid_cols = ['HTSCSecurityID', 'MDDate', 'MDTime', 'MaxPx', 'MinPx', 'PreClosePx', 'NumTrades',
                      'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx',
                      'TotalBuyQty', 'TotalSellQty', 'WeightedAvgBuyPx', 'WeightedAvgSellPx', 'BuyPriceQueue',
                      'BuyOrderQtyQueue', 'SellPriceQueue', 'SellOrderQtyQueue', 'BuyOrderQueue', 'SellOrderQueue',
                      'BuyNumOrdersQueue', 'SellNumOrdersQueue']
        super(OnRecvStockTick, self).__init__(valid_cols)

    def OnMarketData(self, marketdata: MarketData_pb2.MarketData):
        try:
            if marketdata.marketDataType == EMarketDataType.MD_TICK:
                if marketdata.HasField("mdStock"):
                    self.collector[(marketdata.mdStock.HTSCSecurityID,
                                    marketdata.mdStock.MDDate,
                                    marketdata.mdStock.MDTime)] = marketdata.mdStock
        except BaseException as e:
            print("onMarketData error happended!")
            print(e)


class OnRecvKLine(OnRecvMarkertData):
    def __init__(self):
        valid_cols = ['HTSCSecurityID', 'MDDate', 'MDTime', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx', 'NumTrades',
                      'TotalVolumeTrade', 'TotalValueTrade', 'IOPV', 'OpenInterest', 'SettlePrice',
                      'ExchangeDate', 'ExchangeTime', 'KLineCategory']
        super(OnRecvKLine, self).__init__(valid_cols)

    def OnMarketData(self, marketdata: MarketData_pb2.MarketData):
        try:
            if marketdata.marketDataType == EMarketDataType.MD_KLINE_15S or \
               marketdata.marketDataType == EMarketDataType.MD_KLINE_1MIN or \
               marketdata.marketDataType == EMarketDataType.MD_KLINE_15MIN or \
               marketdata.marketDataType == EMarketDataType.MD_KLINE_30MIN or \
               marketdata.marketDataType == EMarketDataType.MD_KLINE_60MIN:
                if marketdata.HasField("mdKLine"):
                    self.collector[(marketdata.mdKLine.HTSCSecurityID,
                                    marketdata.mdKLine.MDDate,
                                    marketdata.mdKLine.MDTime)] = marketdata.mdKLine
        except BaseException as e:
            print("onMarketData error happended!")
            print(e)


def postprocess_playback(data_pd):
    data_pd = data_pd.reset_index(drop=True)
    data_pd['dt'] = pd.to_datetime(data_pd['MDDate'] * 1E9 + data_pd['MDTime'], format='%Y%m%d%H%M%S%f')
    data_pd = data_pd.set_index(['dt', 'HTSCSecurityID']).sort_index()
    data_pd.index.names = ['dt', 'Ticker']
    return data_pd


# 盘中回放接口 --securitylist 和 securityIdList取并集 # Can only query data for one day
def play_back_oneday(stock_list, start_time, stop_time, marketdata_type=EMarketDataType.MD_KLINE_1MIN, exrights_type=MDPlayback_pb2.NO_EXRIGHTS):
    assert isinstance(stock_list, Iterable)
    string_list = mdc_gateway_interface.StrList()
    for item in stock_list:
        string_list.Add(item)
    sort = True # 是否按照mdtime排序
    try:
        pd.to_datetime(start_time, format='%Y%m%d%H%M%S')
        pd.to_datetime(stop_time, format='%Y%m%d%H%M%S')
    except:
        raise AssertionError('Invalid Time Format')
    # params:security_id_list 为标的str集合
    # params:marketdata_type EMarketDataType的枚举值
    # params:exrights_type 为MDPlayback的枚举值
    # params:start_time 为str, 注意格式 "YYYYMMDDHHMMSS"
    # params:stop_time 为str, 注意格式 "YYYYMMDDHHMMSS"
    utils.get_interface().playSortCallback(string_list, start_time, stop_time, marketdata_type, exrights_type, sort)


def subscribe_by_type(security_id_list, security_type_list, marketdata_type_list):
    #element
    # params1: ESecurityIDSource枚举值 --行情源 [ESecurityIDSource.XSHE, ESecurityIDSource.XSHG]
    # params2: ESecurityType的枚举值 --证券类型 [ESecurityType.StockType, ESecurityType.BondType, ESecurityType.FundType]
    # params3: EMarketDataType的枚举值集合 --数据类型 [EMarketDataType.MD_TICK,EMarketDataType.MD_TRANSACTION,EMarketDataType.MD_ORDER]
    assert isinstance(security_id_list, Iterable) and isinstance(security_type_list, Iterable) and isinstance(marketdata_type_list, Iterable)
    assert len(security_id_list) == len(security_type_list) == len(marketdata_type_list)
    security_list = list()
    for security_id, security_type, marketdata_type in zip(security_id_list, security_type_list, marketdata_type_list):
        assert isinstance(marketdata_type, Iterable)
        security_list.append(mdc_gateway_interface.Element(security_id, security_type, marketdata_type))
    action_type = MDSubscribe_pb2.COVERAGE
    utils.get_interface().subscribeByType(action_type, security_list)
    utils.sync()

