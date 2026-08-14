from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

# 这个是读取30分钟数据在日频分组中计算得到30分钟横截面因子
class example_mixfreq(crossFactor):
    def st_factor(self):
        vol = get_minute_1factor('vol', start_datetime=self.cal_start,
                                  end_datetime=self.end, code_list=self.code_list)
        vol = df_match_index_col(vol, self.code_list, self.cal_date_range,'30min')  # np.array
        print(vol.shape)
        return vol

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    group, func = 'sw1', 'cross_mean'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = example_mixfreq(group=group, func=func, author='wyl',factor_name='example_mixfreq', logic='申万一级行业中分钟成交均值',
                        article='20220101-无语证券-一级行业看分钟成交', freq='30mins')
    print(f.result().shape)
    #f.save_result()

