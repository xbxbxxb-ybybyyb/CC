import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


class ReportScoreGrowth(BaseFactor):
    # 因子名称：ReportScoreGrowth
    # 计算公式：过去60个交易日分析师本期评级较上期评级变动的平均值
    # 因子逻辑：分析师评级上调说明公司基本面有提升，会反映到后期股价上
    depend_data = ['FactorData.SUNTIME_cmb_report_score_adjust', 'FactorData.Basic_factor.adjfactor']
    financial_lag = 60

    def calc_single(self, database):
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = adj.columns
        dt = pd.to_datetime(adj.index[-1])
        report = database.depend_data['FactorData.SUNTIME_cmb_report_score_adjust']
        report = report.reset_index()[['stock', 'ORGAN_ID', 'CURRENT_SCORE_ID', 'PREVIOUS_SCORE_ID',
                                       'CURRENT_CREATE_DATE']]
        report = report.sort_values('CURRENT_CREATE_DATE').groupby(['stock', 'ORGAN_ID']).last()
        cur_score = report['CURRENT_SCORE_ID'].map({0.: np.nan, 1.: -2, 2.: -1, 3.: 0, 5.: 1, 7.: 2}).values
        pre_score = report['PREVIOUS_SCORE_ID'].map({0.: np.nan, 1.: -2, 2.: -1, 3.: 0, 5.: 1, 7.: 2}).values
        score_growth = cur_score - pre_score
        ddt = (dt - pd.to_datetime(report['CURRENT_CREATE_DATE'])).dt.days.values
        decay = np.e ** (ddt * np.log(0.5) / 20)
        report['res'] = score_growth * decay
        res = report.groupby('stock')['res'].mean().reindex(stk_code)
        res[res == 0] = np.nan
        return res
