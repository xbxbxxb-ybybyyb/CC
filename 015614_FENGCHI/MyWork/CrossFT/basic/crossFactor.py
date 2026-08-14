from .crossUtils import *
from .crossConfig import *
from .crossOperators import *
import sys
sys.path.append('/data/group/800442/800319')
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_daily_1factor, get_minute_1factor

'''
这里需要自定义的主要有几个方面：
1. 分组因子(group_factor)：    常规的见crossConfig.groups,如果有另类分组就在group_factor中自定义，可以在crossGroups中查找可用的辅助函数
2. 被分组因子（st_factor):     基本上的基础数据计算实现都在这个函数中实现
3. 组内计算方式（group_func):  常规的见crossConfig.funcs,如果有另类分组就在group_func中自定义
4. 自定义计算（calcustomst):   个股===》行业， 行业+个股===》个股，计算了分组然后又跟个股进行了计算，这是时候一般要自定义cal_groupst(self)（如果用到该函数）
5. 返回因子值（result):        定义返回值
6. 因子类名与文件名一致

需要输入的参数：
cross_group：选填
cross_func: 选填
extend_days: 选填，根据因子往前所需要的历史区间
author：必填，fc, hx, lzc, tx, xq
factor_name：必填，因子名称与类名及文件名一致
logic: 必填，输入因子逻辑
article: 选填，'yyyymmdd-券商-研报标题', '无'
freq: 必填，输出因子的频率：daily, 30mins, 5mins, 1min
basic_datas: 如果是index，则写成xx_HS300， 可用指数['SZZZ', 'ZZ1000', 'HS300', 'CYBZ', 'SZ50', 'ZXBZ', 'ZZ800', 'ZZ500','SZCZ']
'''


class crossFactor(object):
    cross_group = None
    cross_func = None
    extend_days = 0
    author = ''
    logic = ''
    article = '无'
    freq = ''
    basic_datas = {'daily': [],  '5mins': [], '1min': []}
    # -------------固定不变-------------------------
    start = cross_range[0]
    end = cross_range[-1]
    mstart = None
    mend = None
    loc = cross_loc
    code_list = np.load(loc + '/basic/code_list.npy').tolist()

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in cross_params:
                self.__dict__[key] = val

        assert (self.mstart == None) | (self.mstart in cross_times['1min'])
        assert (self.mend == None) | (self.mend in cross_times['1min'])

        self.date_range = get_date_range(self.start, self.end)
        self.start = self.date_range[0]
        self.end = self.date_range[-1]
        self.cal_start = get_pre_trade_date(base_date=self.start, offset=self.extend_days)
        self.cal_date_range = get_date_range(self.cal_start, self.end)
        self.factor_name = self.__class__.__name__
        self.start_shift1 = get_pre_trade_date(base_date=self.cal_start, offset=1)
        self.end_shift1 = get_pre_trade_date(base_date=self.end, offset=1)

        try:
            self.load_basic_data()
        except:
            print('读取基础数据有误')

    #############################################################################
    # 个股值==》组值==》个股值 or 组值==》个股值  or 组值+个股值==》个股值
    #############################################################################
    def _clip_data(self, freq, data, shift_exempt):
        '''
        :param freq: int
        :param data: np.array
        :param shift_exempt: 如果不用shift，数据为时间区间开头即可取到，则对对应得时间进行调整往前推一单位（粒度：1min)
        :return:
        '''
        gap = 242//freq -(242%freq==0)
        data_time=cross_times[freq]
        if shift_exempt:
            onemin= cross_times[242]
            data_time = [onemin[onemin.index(data_time[0])-gap]]+data_time[:-1]
        data_time = np.array(data_time)
        if self.mstart:
            data[0,(data_time-self.mstart)<0,:]=np.nan
        if self.mend:
            data[-1,(data_time-self.mend)>0,:]=np.nan
        return data

    def _load_basic_data(self, freq, data, cal_date_range=None, delay=False):
        if not isinstance(cal_date_range, list):
            cal_date_range = self.cal_date_range
        splitdata = data.split('_')
        delayed = False
        if splitdata[-1] in cross_index:
            data, dataindex = '_'.join(splitdata[:-1]), splitdata[-1]
            if cross_basic_datas[data] == 'level1_daily':
                if freq == 'daily':
                    val = get_daily_1factor(data, cal_date_range, type='bench')[dataindex].values.reshape((len(cal_date_range), -1, 1))
                else:
                    if cal_date_range[0] != self.start_shift1 and data not in shift_exempt:
                        cal_date_range = get_date_range(get_pre_trade_date(cal_date_range[0], 1),
                                                        cal_date_range[-1])
                    val = get_daily_1factor(data, cal_date_range, type='bench')[dataindex].values.reshape((len(cal_date_range), -1, 1))
                    delayed = True
                    # print('{}是日频数据，因所需为分钟频，日内数据重复'.format('_'.join(splitdata)))
            elif cross_basic_datas[data] == 'level1_daily_min':
                if freq == 'daily' and data != 'vol':
                    val = get_daily_1factor(data, cal_date_range, type='bench')[dataindex].values.reshape(
                        (len(cal_date_range), -1, 1))
                else:
                    interval = 242 // cross_freqs[freq]
                    name = data if interval == 1 or interval == 242 else data + '_{}m'.format(interval)
                    val = get_minute_1factor(name, cal_date_range[0], cal_date_range[-1],
                                             minute_interval=interval // 242 + interval % 242,
                                             base_date=20100101, type='bench')[
                        dataindex].values.reshape((len(cal_date_range), -1, 1))
            else:
                print(data, '无法读取index值')
        else:
            if cross_basic_datas[data] == 'level1_daily':
                if freq == 'daily':
                    val = get_daily_1factor(data, cal_date_range, self.code_list).values.reshape((len(cal_date_range), -1, len(self.code_list)))
                else:
                    if cal_date_range[0] != self.start_shift1 and data not in shift_exempt:
                        cal_date_range = get_date_range(get_pre_trade_date(cal_date_range[0], 1),
                                                        cal_date_range[-1])

                    val = get_daily_1factor(data, cal_date_range, self.code_list).values.reshape((len(cal_date_range), -1, len(self.code_list)))
                    delayed = True
                    # print('{}是日频数据，因所需为分钟频，日内数据重复'.format('_'.join(splitdata)))
            elif cross_basic_datas[data] == 'level1_daily_min':
                if freq == 'daily':
                    val = get_daily_1factor(data, cal_date_range, self.code_list).values.reshape((len(cal_date_range), -1, len(self.code_list)))
                else:
                    interval = 242 // cross_freqs[freq]
                    name = data if interval == 1 or interval == 242 else data + '_{}m'.format(interval)
                    val = get_minute_1factor(name, cal_date_range[0], cal_date_range[-1],
                                             interval // 242 + interval % 242,
                                             code_list=self.code_list).values.reshape(
                        (len(cal_date_range), -1, len(self.code_list)))
            elif cross_basic_datas[data] == 'level1_min':
                val = load_material(data, cal_date_range[0], cal_date_range[-1], freq,
                                    '/arch1/group/800442/800319/AAcross/basic/datas',
                                    self.code_list).reshape((len(cal_date_range), -1, len(self.code_list)))
            elif cross_basic_datas[data] == 'level2':
                val = load_material(data, cal_date_range[0], cal_date_range[-1], freq,
                                    '/arch1/group/800442/800319/MinFactor/Material',
                                    self.code_list).reshape((len(cal_date_range), -1, len(self.code_list)))

        val = self._clip_data(val.shape[1], val, data in shift_exempt)
        val = cross_resample(val, freq, True,shift=delayed and (data not in shift_exempt))
        if delay and not delayed:
            val = dt_delay(val, 1)[1:, :, :]

        self.database[freq]['_'.join(splitdata)] = val

        #assert (val.shape[0]==len(self.cal_date_range))&(val.shape[1]==cross_freqs[freq])

        #print(data, val.shape, freq, self.freq, delay,delayed,cal_date_range[0], cal_date_range[-1])
        # print('{}: {} loaded'.format(freq, '_'.join(splitdata)), val.shape)

    # @times('数据读取')
    def load_basic_data(self):
        self.database = {'daily': {}, '30mins':{},'5mins': {}, '1min': {}}
        for freq, datas in self.basic_datas.items():
            for data in datas:
                # 低频会主动shift,在写因子中使用cross_resample帮助统一频率，同时选择不shift
                if cross_freqs[freq] < cross_freqs[self.freq] and data not in shift_exempt:
                    cal_date_range = get_date_range(self.start_shift1, self.end)
                    self._load_basic_data(freq, data, cal_date_range, True)
                else:
                    self._load_basic_data(freq, data, delay=False)

    # TODO 增加分钟频分组后，可以考虑不用shift
    def group_factor(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，返回分组值,这里使用前一天的数据是担心日频分组跟分钟频不能对齐
        '''
        if self.cross_group in cross_groups:
            val = load_material(self.cross_group, self.start_shift1, self.end_shift1, 'daily',
                                self.loc + '/basic/groups', require_code_list=self.code_list)
            return val

    def st_factor(self):
        '''
        :return: 1. np.array ,index: datetime, columns: stockpool，返回个股计算组值需要的个股因子
                2.  list(np.array)， index: datetime, columns: stockpool，返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        pass

    def group_func(self):
        '''
        :return: function,主要是分组后组内的个股如何计算,如crossConfig.funcs ,自定义（根据研报中的自定义，一定要注意对nan的处理）
        '''
        if self.cross_func in cross_funcs:
            return eval(self.cross_func)
        return '请定义组内计算方式'

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor = self.st_factor()
        self.stgroup = sameshape(self.factor, self.group_factor())
        calfunc = self.group_func()
        res = st2groupst(self.factor, self.stgroup, calfunc)
        return arr_match_index(res, self.cal_date_range, self.date_range)

    def cal_customst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，
                1.个股===》行业， 行业+个股===》个股，计算了分组然后又跟个股进行了计算，需要用到cal_groupst()
                2. 组值==》个股值，直接获取组值（比如行业指数的因子）,只需要对其进行平铺
        '''
        pass

    #############################################################################
    # 最终返回值
    #############################################################################
    def result(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        pass

