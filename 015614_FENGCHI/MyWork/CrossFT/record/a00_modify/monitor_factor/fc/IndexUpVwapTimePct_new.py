# coding: utf-8
# Author：fengchi863
# Date ：2021/8/19 11:08

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class IndexUpVwapTimePct(crossFactor):
    def st_factor(self):
        close = get_minute_1factor('close', code_list=['SZZZ'], start_datetime=self.cal_start,
                                   end_datetime=self.end, base_date=20100101, type='bench')
        ma = close.groupby('date').expanding().mean().droplevel(0)
        time_flag = (close > ma).applymap(int)
        time_pct = time_flag.groupby('date').expanding().sum() / time_flag.groupby('date').expanding().count()
        time_pct = time_pct.droplevel(0)
        time_pct = time_pct.applymap(float)

        ret = df_match_index_col(time_pct, code_list=time_pct.columns, date_list=self.date_range, freq='1min')
        time_pct = index2st(ret, len(self.code_list))
        return time_pct

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    f = IndexUpVwapTimePct(group=None,
                           func=None,
                           extend_days=0,
                           start=20170101,
                           end=20210531,
                           author='fc',
                           factor_name='IndexUpVwapTimePct',
                           freq='1min',
                           logic='上证指数日内在均线上方的比例',
                           article='市场监控结论')
    f.save_result()
