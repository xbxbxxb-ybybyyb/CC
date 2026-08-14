from Record import Record
import numpy as np
# import StrategyBase
from Position import Position
import pandas as pd
import datetime
from xquant.strategy.backtest.Performance import *


# ---------------回测结果评估-----------------

def get_signal_win_rate(record: Record, window: int, active=False):
    """
    计算信号在未来一段时间窗口的胜率
    :param record: 回测记录 Record对象
    :param window: 计算胜率的未来时长窗口(分钟)
    :param active:
    :return:
    """
    return


def get_sharpe(net_value: pd.DataFrame, risk_free_rate: float = 0):
    """
    计算净值的夏普比率
    :param net_value: 净值
    :param risk_free_rate: 无风险利率
    :return: 夏普比率，float
    """
    Pf = Performance()
    return Pf.Sharpe_Ratio(net_value, end_date=net_value.index[-1], \
                           rf=risk_free_rate, start_date=net_value.index[0])


def get_return(net_value: pd.DataFrame):
    """
    累计收益
    :param net_value:
    :return:
    """
    Pf = Performance()
    return Pf.Annualized_Returns(net_value, start_date=net_value.index[0], \
                                 end_date=net_value.index[-1])


def get_annual_return(net_value: pd.DataFrame):
    """
    年化收益
    :param net_value:
    :return:
    """
    Pf = Performance()
    return Pf.Annualized_Returns(net_value, start_date=net_value.index[0], \
                                 end_date=net_value.index[-1])


def get_volatility(net_value: pd.DataFrame):
    Pf = Performance()
    return Pf.Volatility(net_value, start_date=net_value.index[0], \
                         end_date=net_value.index[-1])


def get_active_return(net_value: pd.DataFrame, benchmark: str = 'ZZ500'):
    return


# -------------因子有效性评估--------------
def get_cross_section_IC(factor_df: pd.DataFrame, window: int):
    """
    计算因子在每个bar上的截面相关性
    :param factor_df: 因子df
    :param window: 预测窗口
    :return:
    """
    return


def get_time_series_IC(factor_df: pd.DataFrame, window: int):
    """
    计算因子在每个bar上的时序相关性
    :param factor_df: 因子df
    :param window: 预测窗口
    :return:
    """
    return


# class FactorEvaluationCrossSection(StrategyBase):
#     """
#     触发式横截面排序买入评估
#     """
#
#     def __init__(self, start: int, end: int, initial_cash: float, universe: list, cost_rate=0.0012, slippage=0.001):
#         super().__init__(start, end, initial_cash, universe, cost_rate, slippage)
#
#     def __init__(self, factor_df: pd.DataFrame):
#         """
#         通过输入因子值DataFrame初始化
#         :param factor_df:
#         """
#         super().__init__(factor_df.index[0], factor_df.index[-1], 10000000, factor_df.columns.tolist())
#
#     def bar_hanle(self, date_time, position: Position):
#         """
#         每个bar买入TopN的股票
#         如何卖出？（日内）
#         :param date_time:
#         :param position:
#         :return:
#         """
#
#     def daily_update(self, date):
#         """
#         每天(月)更新股票池和对象中的数据
#         更新broker数据
#         :return:
#         """
#         pass
#
#     def get_evaluation(self):
#         """
#         调用收益、夏普、胜率、超额收益等评估指标函数，返回评估结果
#         :return:DataFrame
#         """
#
#
# class FactorEvaluationSeries(StrategyBase):
#     """
#     触发式时序排序买入评估
#     """
#
#     def __init__(self, start: datetime.datetime, end: datetime.datetime, initial_cash: float, universe: list,
#                  cost_rate=0.0012, slippage=0.001):
#         super().__init__(start, end, initial_cash, universe, cost_rate, slippage)
#
#     def __init__(self, factor_df: pd.DataFrame):
#         """
#         通过输入因子值DataFrame初始化
#         :param factor_df:
#         """
#         super().__init__(factor_df.index[0], factor_df.index[-1], 10000000, factor_df.columns.tolist())
#
#     def bar_handle(self, date_time, position: Position):
#         """
#         定义当因子指标达到某个阈值的时候买入、卖出
#         :param date_time:
#         :param position:
#         :return:
#         """
#
#     def daily_update(self, date):
#         """
#         每天(月)更新股票池和对象中的数据
#         更新broker数据
#         :return:
#         """
#         pass
#
#     def get_evaluation(self):
#         """
#         计算信号胜率、盈亏比、盈利部分均值、亏损部分均值等指标，返回评估结果
#         :return:DataFrame
#         """
#
#
# def test():
#     cross = FactorEvaluationCrossSection()
#
#
# if __name__ == "__main__":
#     test()
