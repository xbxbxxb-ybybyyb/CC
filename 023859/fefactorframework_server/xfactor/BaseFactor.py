from abc import abstractmethod
import pandas as pd
import numpy as np
from xfactor.FactorDataPrepareUtil import *

class BaseFactor(object):

    strategy_name = "" # 因子策略名/因子库名，saturn/sell 或 jupiter/europa
    factor_name = ""  # 因子名
    owner = ""  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整

    t_1_factor_data_types = []
    factor_subtype = "" # 因子类别 （针对saturn/sell），如: s0(不为空但不存在) s1(存在1m) s(数据为空)
    fill_na_value = float("inf") # fill na所用的值
    need_pre_calculate_T_N = False # 是否需要调用pre_calculate
    t_1_type = "" # T-1日类别
    logic_type = "" # 逻辑类别
    low_cost = "否" # 是否低耗时


    t_day_data = [] # 依赖的T日数据 如 "TTransaction", "T1mTickab_cs"

    # {
    #    name: '', # xdb_order, xdb_trade, xdb_cancel, xdb_tickfull, xdb_tick1s, xdb_tickfulladdorder
    #    lag: 0 # 回看日期，1~N为往前回看1~N天
    # }
    xdb_data = []  # 依赖的T-N高频数据（由系统团队XDB提供， lag=N），格式如上

    # {
    #    name: '',
    #    path: '',
    #    lag: 0,
    #    column: []
    # }
    t_1_factor_data = []  # T-N factor数据，格式如上

    # {
    #    name: '',
    #    path: ''
    # }
    other_t_day_data = []  # 其他添加的数据，每一个数据为一个dict，格式如上


    def __init__(self, **args):
        for k, v in args.items():
            setattr(self, k, v)

    # 因子方法调用顺序(由先到后)： pre_calculate_T_N_data -> prepare_T_data -> calculate

    # 根据T-N相关数据，计算出相关中间变量。
    # 返回值: database
    # 注意1：由于涉及到实盘预计算并存储中间变量，因此限定此方法返回值为一系列键值对生成的series，每个键值对的值仅允许numeric value，
    #       不支持list，dict，df等复杂数据结构。可返回多个键值对。
    # 注意2：返回的数据统一保存至database["pre_calculate_T_N_data"]，形式为dt,Ticker索引的df。
    @abstractmethod
    def pre_calculate_T_N_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        # 例：若当前因子计算产生两个中间变量test1, test2，则跳过计算是返回值应写成如下形式
        if database["skip"] == True:
            return database
        return database

    # 根据T-N相关中间变量，及T日相关数据需求，针对database中T日数据进行预处理。可以直接赋值给database，如 database["zcz"] = True
    # 注意：仅涉及T日数据的因子才可覆写此方法！
    @abstractmethod
    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            df = database['pre_calculate_T_N_data']
            para1 = df['test1'].values[0]
        return database

    # 计算因子值
    @abstractmethod
    def calculate(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        return pd.Series({self.factor_name: 1.1})

    @classmethod
    def get_factor_class_name(cls):
        return cls.__name__




