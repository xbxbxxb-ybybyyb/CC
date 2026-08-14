# coding: utf-8
# Author：fengchi863
# Date ：2021/9/9 21:02


from BombStockStrategy.Factor.basic.crossFactor import crossFactor
from CrossFT.basic.crossUtils import *
from CrossFT.basic.operators import *
from BombStockStrategy.conf.path_conf import factor_path


class LenZtMin(crossFactor):
    extend_days = 10
    author = 'fc'
    start = 20140701
    # start = 20210401
    end = 20210531
    logic = '涨停分钟数'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': [], '1min': ['close']}

    def st_factor(self):
        limit_max = get_daily_1factor('limit_max', code_list=self.code_list, date_list=self.cal_date_range).values
        minute_close = self.database['1min']['close']
        return limit_max, minute_close

    def cal_factor(self):
        limit_max, minute_close = self.st_factor()
        zt_minute = (minute_close == limit_max[:, None, :]).astype(int)
        zt_minute = zt_minute.sum(axis=1)
        ret = arr_match_index(zt_minute, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_factor()


if __name__ == '__main__':
    f = LenZtMin()
    f.check_factor(f.result())
    f.save_result()
