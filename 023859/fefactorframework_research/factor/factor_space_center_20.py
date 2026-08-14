import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_space_center_20(BaseFactor):
    strategy_name = "neptune"
    factor_name = "space_center_20" # TODO 因子名称是类名去掉前面的factor
    fill_na_value = -1e5
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名 TODO 用你的拼音，本来应该是wj，但组里有同事名字缩写也是wj，这里给你改成wenj了
    factor_explain = "20日空间中心度"  # 因子逻辑解释 TODO 请简要填写因子逻辑，如20日空间中心度
    zcz_adjusted = "否"  # 是否针对注册制调整：是/否
    logic_type = ""  # 逻辑类别
    low_cost = "是"  # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 30,  # 注意为正数 TODO lag要适当多取几期
         'column': ['adjfactor', 'close']
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD']  # T-1的h5文件类型列表

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND']  # 和上面t-1_factor_data的name一致
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            df_ori['adj_close'] = df_ori['adjfactor'] * df_ori['close']
            df_ori['adj_pct_chg'] = df_ori['adj_close'].groupby('Ticker', group_keys=False).diff() / df_ori['adj_close']
            ret_table = df_ori['adj_pct_chg'].unstack()

            data_values = ret_table.values
            window_size = 20
            window_ends = np.arange(window_size - 1, len(ret_table))
            window_starts = window_ends - window_size + 1

            result_df = pd.DataFrame(index=ret_table.index, columns=ret_table.columns, dtype=float)

            for end_idx in range(len(window_ends)):
                start_idx = window_starts[end_idx]
                window_data = data_values[start_idx:window_ends[end_idx] + 1, :]  # 形状为 (20, num_stocks)

                # 计算相关系数矩阵
                corr_matrix = np.corrcoef(window_data, rowvar=False)  # 形状为 (num_stocks, num_stocks)

                # 计算每个股票的平均相关系数（排除自身）
                # 对角线设置为NaN以排除自身相关系数
                np.fill_diagonal(corr_matrix, np.nan)

                # 计算每行的平均值，忽略NaN
                avg_corr = np.nanmean(corr_matrix, axis=1)

                # 将结果赋值给当前窗口结束日期
                result_df.iloc[window_ends[end_idx]] = avg_corr

            factors = (1 / (2 * (1 - result_df))).stack()
            df_ori[self.factor_name] = factors

            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df_ori[[self.factor_name]]  # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori  # 纯h5文件的T-1_Factor直接返回df

