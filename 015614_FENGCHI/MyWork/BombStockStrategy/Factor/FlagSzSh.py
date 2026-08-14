# coding: utf-8
# Author：fengchi863
# Date ：2021/9/10 9:04

from BombStockStrategy.Factor.basic.crossFactor import crossFactor
from CrossFT.basic.crossUtils import *
from CrossFT.basic.operators import *
from BombStockStrategy.conf.path_conf import factor_path


class FlagSzSh(crossFactor):
    extend_days = 0
    author = 'fc'
    start = 20140701
    # start = 20210401
    end = 20210531
    logic = '标识类，深圳还是上海'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': []}

    @staticmethod
    def trans_int2flag(x):
        # 0: 上海 1: 深圳
        wincode = trans_int2windcode(x)
        if wincode.startswith('6'):
            return 0
        else:
            return 1

    def st_factor(self):
        flag = list(map(lambda x: self.trans_int2flag(x), self.code_list))
        ret = pd.DataFrame([np.array(flag)] * len(self.cal_date_range),
                           index=self.cal_date_range, columns=self.code_list)
        return ret.values[:, None]

    def result(self):
        ret = self.st_factor()
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret


if __name__ == '__main__':
    f = FlagSzSh()
    f.result()
    f.save_result()
