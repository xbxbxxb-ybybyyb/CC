from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time
import multiprocessing




class CSTurnpureCorrRet(BaseFactor):
    """

    *因子名 : CSTurnpureCorrRet
    *因子功能描述 : 量价齐飞因子变形，计算横截面当日turn与前一日turn回归残差与每日return之间的相关系数,
                
                     
    *因子参数 : close_adj-调整收盘价，turn-换手率，is_valid_raw-是否合法
    *作者 : wulb
    *因子创建日期 : 2019.4.4
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.turn",]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 20
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10
        
    def helper(self, i, dates, turn, factor_result):
        t = time.time()
        cur_date = dates[i]

        cur_turn = turn.iloc[i]
        turn_shift = turn.iloc[i-1]

        day_factor = pd.Series(np.nan, index=cur_turn.index)


        df = pd.DataFrame({'turn':cur_turn.values, 'turn_shift':turn_shift.values}, index=cur_turn.index)
        df = df.dropna()

        x = df.turn.tolist()
        y = df.turn_shift.tolist()
        linear = np.polyfit(x, y, 1)

        cs_residual = df.turn_shift - (linear[0]*df.turn + linear[1])
        day_factor[cs_residual.index] = cs_residual

        factor_result[cur_date] = day_factor


    def calc_single(self, database):
        turn = database.depend_data['FactorData.Basic_factor.turn']
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        # print(turn.index)
        # print(len(turn.index))
        ret = (close_adj - close_adj.shift(1)) / close_adj.shift(1)

        dates = turn.index
        
        num_process = 30
        pool = multiprocessing.Pool(processes=num_process)
        manager = multiprocessing.Manager()

        factor_result = manager.dict()

        res = []
        for i in range(10, len(dates)):
            res.append(pool.apply_async(self.helper, args=(i, dates, turn, factor_result)))

        for i, elem in enumerate(res):
            elem.get()

        pool.close()
        pool.join()
        
        Factor = {}
        for date in dates[10:]:
            Factor[date] = factor_result[date]
        Factor_df = pd.DataFrame(Factor).transpose()
        # Factor_df[is_valid_raw == 0] = np.nan
        Factor_df.index = pd.to_datetime(Factor_df.index)
        
        turn_pure = Factor_df
        
        # turn_pure_corr_ret = turn_pure.rolling(window=10).corr(ret)

        # turn_pure_corr_ret = Util.rolling_corr(turn_pure, ret.iloc[10:,], 10)
        turn_pure_corr_ret = Util.array_coef(turn_pure.iloc[-10:,], ret.iloc[-10:,])
        factor = turn_pure_corr_ret
        # factor = turn_pure_corr_ret.rolling(window=5).mean() / turn_pure_corr_ret.rolling(window=5).std()
        # factor = turn_pure_corr_ret.iloc[-5:,].mean() / turn_pure_corr_ret.iloc[-5:,].std()
        # factor[is_valid_raw == 0] = np.nan
        return factor
        # return factor.iloc[-1,:]
        


    # def calc_single(self, database):
    #     turn = database.depend_data['FactorData.Basic_factor.turn']
    #     close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
    #     # result = self.Mean(amt, 100) / self.Stdev(amt, 100)
    #     amt = amt.iloc[-100:,]
    #     result = amt.mean() / amt.std()
    #     return result
    
            