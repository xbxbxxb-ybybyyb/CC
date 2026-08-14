# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : AmtRatio_5m.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
import bottleneck


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class AmtRatio_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '当日成交量占昨日成交量之比   按昨日 T时刻到今日T时刻为一日计算'
    article = '中信建投	20201023	因子深度研究系列	买卖报单流动性因子构建'
    freq = '5mins'
    basic_datas = {'daily': ['volume'], '30mins': [], '5mins': ['vol'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['5mins']['vol']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        turn = self.st_factor()
        self.group = sameshape(turn, self.group_factor())
        shape = turn.shape
        turn = bottleneck.move_sum(np.concatenate([delay(turn, 1), turn], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]
        group_turn = st2groupst(turn, self.group, cross_sum)
        group_pct = group_turn / delay(group_turn) - 1
        stk_pct = turn / delay(turn) - 1

        return arr_match_index(stk_pct * group_pct, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # for group in groups:
    #     for func in funcs:
    #         print('-------------{}-----------{}-------------'.format(group,func))
    # f = AmtRatio()
    e = time.time()
    # f.result()
    # f.save_result()
    cal_factor()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
