# coding: utf-8
# Author：fengchi863
# Date ：2021/8/18 14:44

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class SkyFloorNum(crossFactor):
    def st_factor(self):
        close = get_minute_1factor('close', start_datetime=self.cal_start, end_datetime=self.end)
        limit_max = get_daily_1factor('limit_max', date_list=self.cal_date_range)
        limit_min = get_daily_1factor('limit_min', date_list=self.cal_date_range)
        limit_max = limit_max.reindex(columns=close.columns)
        limit_min = limit_min.reindex(columns=close.columns)
        a = pd.DataFrame((close.values.reshape(len(limit_max.index), 242, -1) ==
                          limit_max.values[:, None, :]).reshape(len(close.index), -1),
                         index=close.index, columns=close.columns)
        b = pd.DataFrame((close.values.reshape(len(limit_min.index), 242, -1) ==
                          limit_min.values[:, None, :]).reshape(len(close.index), -1),
                         index=close.index, columns=close.columns)
        a = a.applymap(int)
        b = b.applymap(int)
        ab = a.groupby('date').expanding().max().droplevel(0) + b
        tmp = ab.groupby('date').expanding().max() == 2
        tmp = tmp.droplevel(0)
        tmp = tmp.applymap(int)
        factor = df_match_index_col(tmp, self.code_list, self.date_range)
        return factor

    def calc_factor(self):
        factor = self.st_factor()
        ret = np.repeat(np.nansum(factor, axis=2), factor.shape[2]).reshape(factor.shape[0], 242, factor.shape[2])
        return ret

    def result(self):
        return self.calc_factor()


if __name__ == '__main__':
    f = SkyFloorNum(group=None,
                    func=None,
                    extend_days=0,
                    start=20170101,
                    end=20210531,
                    author='fc',
                    factor_name='SkyFloorNum',
                    freq='1min',
                    logic='市场天地板的数量',
                    article='市场监控结论')
    print(f.result())
    f.save_result()
