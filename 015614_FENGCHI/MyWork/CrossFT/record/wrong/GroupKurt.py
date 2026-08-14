# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :GroupKurt.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class GroupKurt(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '收益偏度*分组偏度'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close_badj', 'a_mkt_cap'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['daily']['close_badj'], self.database['daily']['a_mkt_cap']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close_badj, a_mkt_cap = self.st_factor()
        ret = close_badj / delay(close_badj) - 1

        self.group = sameshape(close_badj, self.group_factor())

        weight = a_mkt_cap / st2groupst(a_mkt_cap, self.group, cross_sum)
        group_ret = st2groupst(ret * weight, self.group, cross_sum)

        stk_kurt = pd.DataFrame(ret[:, 0, :]).rolling(self.window).kurt().values[:, None, :]
        group_kurt = pd.DataFrame(group_ret[:, 0, :]).rolling(self.window).kurt().values[:, None, :]

        return arr_match_index(stk_kurt * group_kurt, self.cal_date_range, self.date_range)

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
    f = GroupKurt()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
