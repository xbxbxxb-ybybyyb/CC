import sys
sys.path.insert(1, '/data/user/012245/projects')

from insight.model import EMarketDataType_pb2 as EMarketDataType
from insight.model import MarketData_pb2 as MarketData_pb2
from insight.model import InsightErrorContext_pb2 as InsightErrorContext_pb2
from insight.model import MDPlayback_pb2 as MDPlayback
from insight.model import EMarketDataType_pb2 as EMarketDataType
from insight.model import ESecurityIDSource_pb2 as ESecurityIDSource
from insight.model import ESecurityType_pb2 as ESecurityType
from insight.model import MDSubscribe_pb2 as MDSubscribe
from insight.model import MDPlayback_pb2 as MDPlayback_pb2
from insight.interface import mdc_gateway_interface as mdc_gateway_interface
from insight.data_handle import OnRecvMarkertDataBase
from insight import utils
from multifactor.IO.naming_config import *
import multifactor.utility.common as ut
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.semaphore import ZooKeeper, Semaphore
import multifactor.utility.dt as tdt
import multiprocessing
import pandas as pd
import numpy as np
import os
import sys


def calc_adjfactor_rt(preclose_ps):
    assert isinstance(preclose_ps, pd.Series)
    preclose_ps.name = 'preclose'
    now = pd.to_datetime(pd.Timestamp.now().date())
    prev_date = tdt.get_trading_day_offset(now, -1)[0]
    md = IO.read_data(prev_date, columns=['adjfactor', 'close']).loc[prev_date]
    md = md.join(preclose_ps)
    return md['adjfactor'] * md['close'] / md['preclose']


# This class will pretend to be stdin for my process
class FakeStdin(object):
    def __init__(self):
        self.input = multiprocessing.Queue()

    def readline(self):
        output = self.input.get(timeout=None)
        return output or ''

    def write(self, message):
        self.input.put(message)



class OnRecvMarkertData(OnRecvMarkertDataBase):
    __data_collector = dict()
    __init_timer = None
    __is_data_dumped = False
    __DURATION = 30

    def __init__(self):
        pass

    def OnMarketData(self, marketdata: MarketData_pb2.MarketData):
        ##处理订阅的实时行情数据
        try:
            if marketdata.marketDataType == EMarketDataType.MD_TICK:  # .MD_TICK 快照
                if marketdata.HasField("mdStock"):  # 股票
                    if np.isnan(OnRecvMarkertData.__data_collector.get(marketdata.mdStock.HTSCSecurityID, np.nan)):
                        OnRecvMarkertData.__data_collector[marketdata.mdStock.HTSCSecurityID] = marketdata.mdStock.PreClosePx / 10000.0
                        if OnRecvMarkertData.__init_timer is None:
                            OnRecvMarkertData.__init_timer = pd.Timestamp.now()
                        else:
                            if (pd.Timestamp.now() - OnRecvMarkertData.__init_timer).total_seconds() >= OnRecvMarkertData.__DURATION and not OnRecvMarkertData.__is_data_dumped:
                                preclose_ps = pd.Series(OnRecvMarkertData.__data_collector)
                                ref_date = OnRecvMarkertData.__init_timer.date().strftime('%Y%m%d')
                                print('preclose data collected: num %d at %s' % (len(preclose_ps), ref_date))
                                try:
                                    adjfactor_rt_ps = calc_adjfactor_rt(preclose_ps)
                                    adjfactor_rt_data_path = os.path.normpath(os.path.join(private_h5root, 'market/adjfactor_rt'))
                                    adjfactor_rt_ps.to_hdf(os.path.join(adjfactor_rt_data_path, ref_date + '.h5'), 'adjfactor_rt')
                                    smp = Semaphore(flag_root_path)
                                    smp.touch('adjfactor_rt', ref_date)
                                except Exception as _exp:
                                    print(_exp)
                                finally:
                                    OnRecvMarkertData.__is_data_dumped = True
                    #print("HTSCSecurityID=%s MDTime=%s" % (marketdata.mdStock.HTSCSecurityID, marketdata.mdStock.MDTime))
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
                    if marketdata.mdKLine.HTSCSecurityID in ['000905.SH', '000300.SH']:
                        print(marketdata.mdKLine.HTSCSecurityID, marketdata.mdKLine.MDTime,
                              ' open: ', marketdata.mdKLine.OpenPx,
                              ' close: ', marketdata.mdKLine.ClosePx,
                              ' volume: ', marketdata.mdKLine.TotalVolumeTrade,
                              ' amount: ', marketdata.mdKLine.TotalValueTrade)
                    else:
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


class InsightSample:
    def __init__(self, user_id):
        # 流量与日志开关设置
        # open_trace trace流量日志开关 # params:open_file_log 本地日志文件开关  # params:open_cout_log 控制台日志开关
        open_trace = True
        open_file_log = True
        open_cout_log = False
        utils.get_interface().init(open_trace, open_file_log, open_cout_log)

        # 注册回调和接管日志
        # 1.注册回调接口，不注册无法接收数据、处理数据。订阅不同类型的行情，必须实现指定的回调接口。
        callback = OnRecvMarkertData()
        utils.get_interface().setCallBack(callback)

        # 2.接管日志
        # 若想关闭系统日志,自我处理日志,打开本方法
        # 打开本方法后,日志在insightlog.py的PyLog类的方法log(self,line)中也会体现,其中 line为日志内容）
        # use_init = True 系统日志以 utils.get_interface().init 配置的方式记录
        # use_init = False 系统不再记录或打印任何日志,日志只有自行处理部分处理
        ### 以下是示例 ###
        # use_init = True
        # utils.get_interface().own_deal_log(use_init)
        utils.login(user_id)

    def __del__(self):
        utils.fini()

    def subscribe_by_type(self, security_type=ESecurityType.StockType, data_type=EMarketDataType.MD_KLINE_1MIN):
        # 订阅行情接口调用，调用回调类中的OnMarketData方法
        # params1: ESecurityIDSource枚举值 --行情源
        # security_type: ESecurityType的枚举值 --证券品种类型
        # data_type: EMarketDataType的枚举值集合 --行情数据类型

        # 沪深 - 股票
        element0 = mdc_gateway_interface.Element(ESecurityIDSource.XSHE, security_type, [data_type])
        element1 = mdc_gateway_interface.Element(ESecurityIDSource.XSHG, security_type, [data_type])

        securitylist = [element0, element1]
        # MDSubscribe.COVERAGE模式，覆盖上一次的订阅内容
        action_type = MDSubscribe.COVERAGE
        utils.get_interface().subscribeByType(action_type, securitylist)
        utils.sync()

    # 盘中回放接口 --securitylist 和 securityIdList取并集
    # Can only query data for one day
    def play_back_oneday(self, stock_list, start_time, stop_time, data_type=EMarketDataType.MD_KLINE_1MIN,
                         sort=False):
        """
        :param stock_list: security_id_list 为 标的str集合
        :param start_time: 为 str,注意格式
        :param stop_time: 为 str,注意格式
        :param data_type: EMarketDataType的枚举值
        :param sort: 是否对所有数据按mdtime排序
        :return:
        """
        # 回放行情接口调用，调用回调类中的OnPlaybackPayload方法
        string_list = mdc_gateway_interface.StrList()
        for stock in stock_list:
            string_list.Add(stock)

        exrights_type = MDPlayback.NO_EXRIGHTS
        utils.get_interface().playSortCallback(string_list, start_time, stop_time, data_type, exrights_type, sort)


def retrieve_preclose_helper():
    sys.stdin = FakeStdin()
    insight = InsightSample(user_id='013150')  #订阅实时行情数据*
    insight.subscribe_by_type(security_type=ESecurityType.StockType, data_type = EMarketDataType.MD_TICK)


if __name__ == '__main__':
    proc = multiprocessing.Process(target=retrieve_preclose_helper, args=())
    proc.start()
    # Terminate the process
    ref_date = pd.Timestamp.now().date().strftime('%Y%m%d')
    smp = Semaphore(flag_root_path)
    if smp.wait(['adjfactor_rt'], ref_date, gap=1):
        print('terminating subprocess')
        proc.terminate()  # sends a SIGTERM

