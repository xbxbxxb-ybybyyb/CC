from CrossFT.basic.crossUtils import *
from CrossFT.basic.crossConfig import *
from CrossFT.basic.crossOperators import *
from BombStockStrategy.conf.path_conf import factor_path
import sys

sys.path.append('/data/group/800442/800319')
from dataApi.getData import *

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
    artical = '无'
    freq = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': []}
    # -------------固定不变-------------------------
    start = cross_range[0]
    end = cross_range[-1]
    loc = cross_loc
    save_loc = factor_path

    # def __init__(self, group=None, func=None, extend_days=0, start=20170101, end=20210531, author='wyl',
    #              factor_name='', logic='', article='无', freq='',
    #              basic_datas={'daily': [], '30mins': [], '5mins': [], '1min': []},
    #              loc='/data/group/800442/800319/AAcross'):
    #     '''
    #           :param group: crossConfig.groups或自定义
    #           :param func: crossConfig.funcs或自定义
    #           :param extend_days: 从起始日期往前推N日，考虑到rolling等问题需要往前读取数据
    #           :param start: 起始日期，注意读取个股的时间区间，要保证计算区间中没有全市场全是np.nan
    #           :param end: 终止日期
    #           :param author: 自己名字缩写，fc, hx, lzc, wyl
    #           :param factor_name: 因子名称，一般是个人名加上数字
    #           :param logic: 因子逻辑
    #           :param article: 来自哪篇文章，yyyymmdd-券商-研报标题
    #           :param freq: 输出因子的频率：daily, 30mins, 5mins, 1min
    #           :param loc: 横截面相关数据存储地，不用管
    #           '''
    #     self.date_range = get_date_range(start, end)
    #     self.start = self.date_range[0]
    #     self.end = self.date_range[-1]
    #     self.cal_start = get_pre_trade_date(base_date=self.start, offset=extend_days)
    #     self.cal_date_range = get_date_range(self.cal_start, end)
    #     self.cross_group = group
    #     self.cross_func = func
    #     self.loc = loc
    #     self.author = author
    #     self.factor_name = self.__class__.__name__
    #     self.logic = logic
    #     self.article = article
    #     self.freq = freq
    #     self.code_list = np.load(loc + '/basic/code_list.npy').tolist()
    #     self.basic_datas = basic_datas
    #     try:
    #         self.load_basic_data()
    #     except:
    #         print('读取基础数据有误')
    #
    def __init__(self):
        self.date_range = get_date_range(self.start, self.end)
        self.start = self.date_range[0]
        self.end = self.date_range[-1]
        self.cal_start = get_pre_trade_date(base_date=self.start, offset=self.extend_days)
        self.cal_date_range = get_date_range(self.cal_start, self.end)
        self.factor_name = self.__class__.__name__
        self.code_list = np.load(self.loc + '/basic/code_list.npy').tolist()
        try:
            self.load_basic_data()
        except:
            print('读取基础数据有误')

    #############################################################################
    # 个股值==》组值==》个股值 or 组值==》个股值  or 组值+个股值==》个股值
    #############################################################################
    @times('数据读取')
    def load_basic_data(self):
        self.database = {'daily': {}, '30mins': {}, '5mins': {}, '1min': {}}
        for freq, datas in self.basic_datas.items():
            for data in datas:
                splitdata = data.split('_')
                if splitdata[-1] in cross_index:
                    data, dataindex = '_'.join(splitdata[:-1]), splitdata[-1]
                    if cross_basic_datas[data] == 'level1_daily':
                        val = get_daily_1factor(data, self.cal_date_range, type='bench')[dataindex].values
                        if freq != 'daily':
                            print('{}是日频数据，因所需为分钟频，日内数据重复'.format('_'.join(splitdata)))
                    elif cross_basic_datas[data] == 'level1_daily_min':
                        if freq == 'daily':
                            val = get_daily_1factor(data, self.cal_date_range, type='bench')[dataindex].values.reshape(
                                (len(self.cal_date_range), -1, 1))
                        else:
                            interval = 242 // cross_freqs[freq]
                            name = data if interval == 1 or interval == 242 else data + '_{}m'.format(interval)
                            val = get_minute_1factor(name, self.cal_start, self.end,
                                                     minute_interval=interval // 242 + interval % 242,
                                                     base_date=20100101, type='bench')[
                                dataindex].values.reshape((len(self.cal_date_range), -1, 1))
                    else:
                        print(data, '无法读取index值')
                else:
                    if cross_basic_datas[data] == 'level1_daily':
                        val = get_daily_1factor(data, self.cal_date_range, self.code_list).values
                        if freq != 'daily':
                            print('{}是日频数据，因所需为分钟频，日内数据重复'.format('_'.join(splitdata)))
                    elif cross_basic_datas[data] == 'level1_daily_min':
                        if freq == 'daily':
                            val = get_daily_1factor(data, self.cal_date_range, self.code_list).values
                        else:
                            interval = 242 // cross_freqs[freq]
                            name = data if interval == 1 or interval == 242 else data + '_{}m'.format(interval)
                            val = get_minute_1factor(name, self.cal_start, self.end, interval // 242 + interval % 242,
                                                     code_list=self.code_list).values.reshape(
                                (len(self.cal_date_range), -1, len(self.code_list)))
                    elif cross_basic_datas[data] == 'level1_min':
                        val = load_material(data, self.cal_start, self.end, freq,
                                            '/arch1/group/800442/800319/AAcross/basic/datas',
                                            self.code_list).reshape((len(self.cal_date_range), -1, len(self.code_list)))
                    elif cross_basic_datas[data] == 'level2':
                        val = load_material(data, self.cal_start, self.end, freq,
                                            '/arch1/group/800442/800319/MinFactor/Material',
                                            self.code_list).reshape((len(self.cal_date_range), -1, len(self.code_list)))
                val = cross_resample(val, freq)
                self.database[freq]['_'.join(splitdata)] = val
                print('{}: {} loaded'.format(freq, '_'.join(splitdata)), val.shape)

    def check(self):
        if self.author not in ['fc', 'hx', 'lzc', 'tx', 'xq', 'wyl']:
            print('请重新定义author')
            return False
        filename = sys.argv[0].split('/')[-1].split('.')[0]
        classname = self.__class__.__name__
        if len(set([filename, classname])) > 1 and filename != 'crosstest':
            print('文件名、类名、因子名命名不一致')
            return False
        if len(self.logic) == 0:
            print('请输入因子逻辑')
            return False
        if self.freq not in ['daily', '30mins', '5mins', '1min']:
            print('因子频率输入错误')
            return False
        test_range1 = get_date_range(cross_range[0], cross_range[1])
        if int(self.start) != int(test_range1[0]) or int(self.end) != int(test_range1[-1]):
            print('请重新输入回测起始或终止日期')
            return False

        subdatas = []
        for val in self.basic_datas.values():
            for x in val:
                data = x.split('_')
                if data[-1] in cross_index:
                    data = '_'.join(data[:-1])
                else:
                    data = '_'.join(data)
                subdatas.append(data in cross_basic_datas.keys())

        # if len(subdatas) and not all(subdatas):
        #     print('自动读取基础数据有误')
        #     return False
        return True

    #TODO 增加分钟频分组后，可以考虑不用shift
    def group_factor(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，返回分组值,这里使用前一天的数据是担心日频分组跟分钟频不能对齐
        '''
        start_shift1 = get_pre_trade_date(base_date=self.cal_start, offset=1)
        end_shift1 = get_pre_trade_date(base_date=self.end, offset=1)
        if self.cross_group in cross_groups:
            val = load_material(self.cross_group, start_shift1, end_shift1, 'daily',self.loc + '/basic/groups')
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

    @times('因子计算加存储')
    def save_result(self):
        '''
        :return: 调用后直接存储因子计算值
        '''
        if self.check():
            res = self.result()
            try:
                res_shape = res.shape
                if res_shape[0] == len(self.date_range) and res_shape[-1] == len(self.code_list):
                    if len(res_shape) == 2 or (len(res_shape) == 3 and res_shape[1] == cross_freqs[self.freq]):
                        save_loc = self.save_loc + '{}/{}_{}'.format(self.freq, self.start, self.end)
                        update_folder(save_loc)
                        np.save(save_loc + '/{}.npy'.format(self.factor_name), res)
                        print(self.factor_name, '因子存储成功')
                    else:
                        print(self.factor_name, '数据time有误')
                else:
                    print(self.factor_name, '数据shape有误')
            except:
                print(self.factor_name, '数据格式有误')
        else:
            print(self.factor_name, '因子存储失败，请查找原因')

    # 添加的工具函数
    @staticmethod
    def check_factor(factor):
        num = factor.shape[0] * factor.shape[1] * factor.shape[2]
        nan_pct = np.isnan(factor).sum() / num
        inf_pct = np.isinf(factor).sum() / num
        diff_len = len(np.unique(factor))
        print('nan pct is %.2f\ninf pct is %.2f\ndiff values is %d/%d' % (nan_pct, inf_pct, diff_len, num))
