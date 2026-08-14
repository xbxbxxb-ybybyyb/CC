# coding: utf-8
# Author：fengchi863
# Date ：2021/8/25 10:43

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class SZCZUpVwapTimePct(crossFactor):
    extend_days = 0
    author = 'fc'
    factor_name = 'SZCZUpVwapTimePct'
    freq = '1min'
    logic = '深证成指日内在均线上方的比例'
    article = '市场监控结论'

    def st_factor(self):
        close = get_minute_1factor('close', code_list=['SZCZ'], start_datetime=self.cal_start,
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
    f = SZCZUpVwapTimePct()
    f.save_result()
