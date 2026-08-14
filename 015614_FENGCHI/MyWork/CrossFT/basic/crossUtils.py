import sys

sys.path.append('/data/group/800442/800319')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import numpy as np
import pandas as pd
import signal
from .crossConfig import *
from .operators import dt_delay, dt_mean, dt_max, dt_min
import warnings
import importlib
import multiprocessing as mp
import requests
import json
import os
import time
from .crosslog import logs


def st2groupst(indicator, group, func, **kwargs):
    '''
    indicator:个股指标，用于合成组别指标
    group:个股分组情况，shape要和indicator相同
    func：组内计算方法, nansum, nanmean,nanmax,nanmin,nanmedian,nanstd,nanvar,nanquantile,自定义
    return: 返回的是个股横截面指标，index=time, columns= stock_pool
    '''
    groups = np.unique(group[np.isfinite(group)])
    shape = indicator.shape
    res = np.full(shape, np.nan)
    for g in groups:
        val = group == g
        if len(shape) == 2:
            res = np.where(val, func(indicator, len(shape) - 1, val, **kwargs)[:, None], res)
        elif len(shape) == 3:
            res = np.where(val, func(indicator, len(shape) - 1, val, **kwargs)[:, :, None], res)
    return res


def st2group(indicator, group, func, **kwargs):
    '''
    indicator:个股指标，用于合成组别指标
    group:个股分组情况，shape要和indicator相同
    func：组内计算方法, nansum, nanmean,nanmax,nanmin,nanmedian,nanstd,nanvar,自定义
    return: 返回的是组指标，index=time，columns=np.arange(groups)
    '''
    groups = np.unique(group[np.isfinite(group)])
    shape = indicator.shape
    res = np.full((*shape[:-1], int(max(groups) + 1)), np.nan)
    for g in groups:
        val = group == g
        if len(shape) == 2:
            res[:, int(g)] = func(indicator, len(shape) - 1, val,
                                  **kwargs)  # func(np.where(group == g, indicator, np.nan), axis=len(shape) - 1)#
        elif len(shape) == 3:
            res[:, :, int(g)] = func(indicator, len(shape) - 1, val,
                                     **kwargs)  # func(np.where(group == g, indicator, np.nan), axis=len(shape) - 1)#
    return res


def group2st(group, groupval):
    '''
    这个主要是与st2group结合使用
    group:个股分组情况
    groupval:每个分组对应的值，index与group相同
    '''
    shape = group.shape
    groups = np.unique(group[np.isfinite(group)])
    res = np.full(group.shape, np.nan)
    for g in groups:
        if len(shape) == 2:
            res = np.where(group == g, groupval[:, int(g)][:, None], res)
        elif len(shape) == 3:
            res = np.where(group == g, groupval[:, :, int(g)][:, :, None], res)
    return res


def index2st(index, code_num):
    '''
    :param index: np.array, 2d，3d
    :param code_num: len(code_list
    :return: np.array, index= time, columns = code
    '''
    if index.shape[-1] == 1:
        return np.repeat(index, code_num, axis=-1)
    else:
        print('输入数据非1列')


def sameshape(st, group):
    '''
   是指columns相同，index层数不同=====>频率对齐
    '''
    st_shape = st.shape
    group_shape = group.shape
    if st_shape[-1] == group_shape[-1] and st_shape[0] == group_shape[0]:
        if len(st_shape) == len(group_shape):
            if len(st_shape) == 2:
                return group
            elif len(st_shape) == 3:
                if st_shape[1] % group_shape[1] == 0:
                    return np.repeat(group, st_shape[1] / group_shape[1], axis=1).reshape(st_shape)
                else:
                    print('数据频率无法处理')
            else:
                print('数据频率无法处理')
        elif len(st_shape) > len(group_shape):
            return np.repeat(group, st_shape[1], axis=0).reshape(st_shape)
        else:
            return group[:, 0, :]  # 这里假设就取当天最早的分组作为当天的分组
    return '时间区间或者股票数没有对齐'


def arr_match_index(arr, arr_date_list=None, date_list=None, arr_code_list=None, code_list=None):
    # 这里都假设 date_list, code_list都是按照顺序排列的, list
    shape = arr.shape
    if len(shape) < 2:
        # 这个时候arr为空，直接返回所需形状的np.nan
        res = np.full((len(date_list), 1, len(code_list)), np.nan)
        return res
    elif len(shape) == 2:
        arr = arr[:, None, :]
    if (arr_date_list == None or (arr_date_list != None and shape[0] == len(arr_date_list))) and (
            arr_code_list == None or (arr_code_list != None and shape[-1] == len(arr_code_list))):
        if arr_date_list != None and arr_code_list != None:
            res = np.full((len(date_list), arr.shape[1], len(code_list)), np.nan)
            arr_date_list = list(map(int, arr_date_list))
            arr_code_list = list(map(int, arr_code_list))
            arr = arr[np.argsort(arr_date_list), :, :][:, :, np.argsort(arr_code_list)]
            arr_date_list = sorted(arr_date_list)
            arr_code_list = sorted(arr_code_list)

            validr = set(arr_date_list) & set(date_list)
            validc = set(arr_code_list) & set(code_list)
            list_idx = np.array(
                [[x, y] for x in np.arange(len(date_list))[list(map(lambda x: x in validr, date_list))] \
                 for y in np.arange(len(code_list))[list(map(lambda x: x in validc, code_list))]])

            arr_idx = np.array(
                [[x, y] for x in np.arange(len(arr_date_list))[list(map(lambda x: x in validr, arr_date_list))] \
                 for y in np.arange(len(arr_code_list))[list(map(lambda x: x in validc, arr_code_list))]])
            if len(list_idx) and len(arr_idx):
                res[list_idx[:, 0], :, list_idx[:, 1]] = arr[arr_idx[:, 0], :, arr_idx[:, 1]]
        elif arr_date_list != None:
            res = np.full((len(date_list), *arr.shape[1:]), np.nan)
            arr_date_list = list(map(int, arr_date_list))
            arr = arr[np.argsort(arr_date_list), :, :]
            arr_date_list = sorted(arr_date_list)
            validr = set(arr_date_list) & set(date_list)
            res[list(map(lambda x: x in validr, date_list)), :, :] = arr[list(
                map(lambda x: x in validr, arr_date_list)), :, :]
        elif arr_code_list != None:
            res = np.full((*arr.shape[:-1], len(code_list)), np.nan)
            arr_code_list = list(map(int, arr_code_list))
            arr = arr[:, :, np.argsort(arr_code_list)]
            arr_code_list = sorted(arr_code_list)
            validc = set(arr_code_list) & set(code_list)
            res[:, :, list(map(lambda x: x in validc, code_list))] = arr[:, :, list(
                map(lambda x: x in validc, arr_code_list))]

        # if len(shape) == 2:
        #     res = res.reshape((len(res), -1))
        return res
    else:
        print('arr数据形状与arr_date_list或arr_code_list不对应')


# 已经使用数据进行检验
def cross_resample(arr, freq, dropbegin=False, mincompress='last', dailycompress='last', shift=False):
    '''
    :param arr:  np.array
    :param freq:
    :param dropbegin:
    :param mincompress: 针对于降频：'last','mean','max','min'
    :param dailycompress: 针对于降频：'last','mean','max','min','openning'(9.30-9:59), 'closing'(14:27-14:56
    :return: 'daily': 1, '30mins': 8, '5mins': 48, '1min': 242
    '''

    shape = arr.shape
    if len(shape) == 1:
        res = arr[:, None, None]
    elif len(shape) == 2:
        res = arr[:, None, :]
    else:
        res = arr
    shape = res.shape
    gap = cross_freqs[freq]
    if shape[1] > gap:
        if gap == 1:
            if dailycompress == 'last':
                res = res[:, -1:, :]
            elif dailycompress == 'mean':
                res = np.nanmean(res, axis=1, keepdims=True)
            elif dailycompress == 'max':
                res = np.nanmax(res, axis=1, keepdims=True)
            elif dailycompress == 'min':
                res = np.nanmin(res, axis=1, keepdims=True)
            elif dailycompress == 'openning':
                if shape[1] == 242:
                    res = np.nanmean(res[:, 1:31, :], axis=1, keepdims=True)
                elif shape[1] == 48:
                    res = np.nanmean(res[:, :6, :], axis=1, keepdims=True)  # 9:35-10:00
                elif shape[1] == 8:
                    res = res[:, :1, :]
            elif dailycompress == 'closing':
                if shape[1] == 242:
                    res = np.nanmean(res[:, -34:-4, :], axis=1, keepdims=True)
                elif shape[1] == 48:
                    res = np.nanmean(res[:, -7:-1, :], axis=1, keepdims=True)  # 14.30-14:55
                elif shape[1] == 8:
                    res = res[:, -2:-1, :]
            else:
                print('Arr 不能降维')
                return
        else:
            if mincompress == 'last':
                if shape[1] == 242 and gap != 1:
                    res = res[:, 1::240 // gap, :][:, 1:, :]
                elif shape[1] == 48 and gap == 8:
                    res = res[:, 5::shape[1] // gap, :]
            elif mincompress == 'mean':
                if shape[1] == 242 and gap != 1:
                    res = dt_mean(res, 240 // gap)[:, 1::240 // gap, :][:, 1:, :]
                elif shape[1] == 48 and gap == 8:
                    res = dt_mean(res, shape[1] // gap)[:, 5::shape[1] // gap, :]
            elif mincompress == 'max':
                if shape[1] == 242 and gap != 1:
                    res = dt_max(res, 240 // gap)[:, 1::240 // gap, :][:, 1:, :]
                elif shape[1] == 48 and gap == 8:
                    res = dt_max(res, shape[1] // gap)[:, 5::shape[1] // gap, :]
            elif mincompress == 'min':
                if shape[1] == 242 and gap != 1:
                    res = dt_min(res, 240 // gap)[:, 1::240 // gap, :][:, 1:, :]
                elif shape[1] == 48 and gap == 8:
                    res = dt_min(res, shape[1] // gap)[:, 5::shape[1] // gap, :]
            else:
                print('arr 不能降维')
                return
    elif shape[1] < gap:
        if shift:
            res = dt_delay(res, 1)
        if shift and dropbegin:
            res = res[1:, :, :]
        res_end = res[:, -1, :]
        if shape[1] == 1:
            res = np.repeat(res, gap // shape[1], axis=1)
            res[:, -1, :] = res_end
        elif gap == 48:
            res1 = np.full((shape[0], 48, shape[-1]), np.nan)
            res1[:, :-1, :] = np.repeat(res, gap // shape[1], axis=1)[:, 1:, :]
            res1[:, -1, :] = res_end
            res = res1.copy()
        elif gap == 242 and 240 % shape[1] == 0:
            res1 = np.full((shape[0], 242, shape[-1]), np.nan)
            res1[:, 1:-1, :] = np.repeat(res, gap // shape[1], axis=1)
            res1[:, 0, :] = res1[:, 1, :]
            res1[:, -1, :] = res_end
            res = res1.copy()
        else:
            print('arr无法升维')
            return
    return res

    def save(self, df, name, **kwargs):
        path = os.path.join(self.save_path, name)
        index, columns = df.index, df.columns
        if index.dtype == 'int':
            pass
        elif index.dtype == 'O':
            df.index = index.astype(int)
        else:
            df.index = index.map(lambda x: int(x.strftime('%Y%m%d')))

        if columns.dtype == 'int':
            pass
        else:
            df.columns = df.columns.map(lambda x: int(x.split('.')[0]))


# 已经使用数据进行检验
def df_match_index_col(df, code_list, date_list, freq='daily', return_type='array'):
    '''
    :param df: DataFrame,index=time,columns=stock，默认输入的数据为日频或者1分钟频率
    :param code_list: 股票池,int64
    :param date_list: 日期池，只是yyyymmdd，int64
    :param freq: 因子的频率：daily, 30mins, 5mins, 1min
    :return:对应code_list,date_list的np.array
    '''
    try:
        res = df.loc[date_list, code_list]
        if return_type == 'array':
            if len(res.index.names) == 1:
                shape = (len(res), 1, len(res.columns))
            else:
                shape = (len(res.index.levels[0]), -1, len(res.columns))
            res = res.values.reshape(shape)
        return res
    except:
        df_index, df_columns = df.index, df.columns
        if df_columns.dtype != 'int64':
            df.columns = df.columns.map(lambda x: int(str(x).split('.')[0]))

        if len(df.index.names) == 1:
            if df_index.dtype != 'int64':
                df.index = df.index.map(int)
            res_index = date_list
            arr_index, arr_columns = df_index.tolist(), df_columns.tolist()
            shape = (len(df), 1, len(df_columns))
        else:
            names = df_index.names
            df = df.reset_index()
            df[names] = df[names].astype(int)
            df = df.set_index(names, drop=True)
            res_index = pd.MultiIndex.from_product([date_list, df_index.levels[1]])
            arr_index, arr_columns = df_index.levels[0].tolist(), df_columns.tolist()
            shape = (len(df_index.levels[0]), -1, len(df.columns))

        res = arr_match_index(df.values.reshape(shape), arr_index, date_list, arr_columns, code_list).reshape(
            len(date_list), -1, len(code_list))

        if return_type != 'array':
            return pd.DataFrame(res.reshape((-1, len(code_list))), index=res_index, columns=code_list)
        return res


# 目前只是针对group，barra group数据，level1_min, level2都在1min,5min,30min,daily频率下在一个时间窗口上比较直接读取和用load_material读取，都保证对得上
def load_material(name, start_date, end_date, freq='1min', address='/arch1/group/800442/800319/AAcross',
                  require_code_list=None, info_address=None, org_freq=None):
    dtype = 'float32'
    unit_size = 4
    if not org_freq:
        middle_len = 1 if name in cross_groups else 242
    else:
        middle_len = cross_freqs[org_freq]
    if not info_address:
        code_list = pd.read_pickle(
            address.replace("Material", '') + 'DateCode/code_list.pkl') if name in level2 else np.load(
            address + '/code_list.npy').tolist()
        date_list = np.load(
            address.replace("Material", '') + 'DateCode/date_list.npy').tolist() if name in level2 else np.load(
            address + '/date_list.npy').tolist()
    else:
        code_list = np.load(info_address + '/code_list.npy').tolist()
        date_list = np.load(info_address + '/date_list.npy').tolist()
    code_num = len(code_list)
    date_range = get_date_range(start_date, end_date)
    start_date, end_date = date_range[0], date_range[-1]
    if start_date in date_list:
        start_idx = date_list.index(start_date)
        start_before = 0
    else:
        start_idx = 0
        start_before = date_range.index(date_list[0])
    if end_date in date_list:
        end_idx = date_list.index(end_date)
        end_after = 0
    else:
        end_idx = len(date_list) - 1
        end_after = len(date_range) - 1 - date_range.index(date_list[-1])

    offset = start_idx * middle_len * code_num * unit_size + 128

    shape = (end_idx + end_after - start_idx + start_before + 1, cross_freqs[freq], code_num)
    arr = np.full(shape, np.nan, dtype=dtype)

    if middle_len == 1:
        fp = np.memmap(f'{address}/{name}.npy', dtype=dtype, offset=offset,
                       shape=(end_idx - start_idx + 1, 1, code_num))
    else:
        fp = np.memmap(f'{address}/{name}.npy', dtype=dtype, offset=offset,
                       shape=(end_idx - start_idx + 1, 242, code_num))

    arr[start_before:len(arr) - end_after, :, :] = cross_resample(fp, freq, shift=True)
    # if freq == '1min':
    #     arr[start_before:len(arr) - end_after, :, :] = fp[:, :, :]
    # elif freq == 'daily':
    #     arr[start_before:len(arr) - end_after, :, :] = fp[:, -1:, :]
    # else:
    #     arr[start_before:len(arr) - end_after, :, :] = cross_resample(fp,freq,shift=True)
    del fp
    if require_code_list != None:
        arr = arr_match_index(arr, arr_code_list=code_list, code_list=require_code_list)

    return arr


###########################################################################
# 辅助函数
###########################################################################
def time_limit(set_time, callback):
    # '''set_time是设置的时间限制，callback是程序运行后执行的函数'''
    def wraps(func):
        # 收到信号SIGALRM后的回调函数，参数1是信号的数字，参数2是the interrupted stack frame.
        def handler(signum, frame):
            raise RuntimeError()

        def deco(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(set_time)
                res = func(*args, **kwargs)

                signal.alarm(0)
                return res
            except RuntimeError as e:
                # callback()  ##如果不想要超时跳转，那么直接删除callback()和对应的参数
                print('time_out')

        return deco

    return wraps


def after_timeout():  # 超时后的处理函数
    print("Time out!")
    return


def update_folder(loc):
    # p = Path(loc)
    # p.mkdir(parents=True)
    temp_dir = loc.split('/')[::-1]
    temp = '/'
    while len(temp_dir):
        temp += temp_dir.pop() + '/'
        if not os.path.exists(temp):
            os.mkdir(temp)


def send_message(users, msg):
    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    for user in users:
        data = {"touser": user,
                "msgtype": "text",
                "agentid": 1000033,
                "text": {"content": msg}}
        json_data = json.dumps(data)
        requests.post(post_url, json_data)


def move_func(func, a, window, min_count=None, axis=-1, **kwargs):
    "Generic moving window function implemented with a python loop."
    a = np.array(a, copy=False)
    if min_count is None:
        mc = window
    else:
        mc = min_count
        if mc > window:
            msg = "min_count (%d) cannot be greater than window (%d)"
            raise ValueError(msg % (mc, window))
        elif mc <= 0:
            raise ValueError("`min_count` must be greater than zero.")
    if a.ndim == 0:
        raise ValueError("moving window functions require ndim > 0")
    if axis is None:
        raise ValueError("An `axis` value of None is not supported.")
    if window < 1:
        raise ValueError("`window` must be at least 1.")
    if window > a.shape[axis]:
        raise ValueError("`window` is too long.")
    if issubclass(a.dtype.type, np.inexact):
        y = np.empty_like(a)
    else:
        y = np.empty(a.shape)
    idx1 = [slice(None)] * a.ndim
    idx2 = list(idx1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i in range(a.shape[axis]):
            win = min(window, i + 1)
            idx1[axis] = slice(i + 1 - win, i + 1)
            idx2[axis] = i
            y[idx2] = func(a[idx1], axis=axis, **kwargs)
    idx = _mask(a, window, mc, axis)
    y[idx] = np.nan
    return y


def _mask(a, window, min_count, axis):
    n = (a == a).cumsum(axis)
    idx1 = [slice(None)] * a.ndim
    idx2 = [slice(None)] * a.ndim
    idx3 = [slice(None)] * a.ndim
    idx1[axis] = slice(window, None)
    idx2[axis] = slice(None, -window)
    idx3[axis] = slice(None, window)
    nidx1 = n[idx1]
    nidx1 = nidx1 - n[idx2]
    idx = np.empty(a.shape, dtype=np.bool)
    idx[idx1] = nidx1 < min_count
    idx[idx3] = n[idx3] < min_count
    return idx


def times(name):
    def wraps(func):
        def call_fun(*args, **kwargs):
            start_time = time.time()
            res = func(*args, **kwargs)
            end_time = time.time()
            print(name + '程序用时：%s秒' % round(end_time - start_time, 4))
            return res

        return call_fun

    return wraps


def forward_fill(arr, axis, zero_fill=True):
    arr = arr.swapaxes(axis, -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis=-1, out=idx)

    out = arr[tuple(np.arange(idx.shape[x])[(None,) * x + (slice(None),) + (None,) * (idx.ndim - x - 1)]
                    for x in range(idx.ndim - 1)) + (idx,)]
    out = out.swapaxes(axis, -1)
    return out


#########################################################
# cal_factor,已经对比直接计算和分部计算结果差异，差异主要来源于np自身精度
#########################################################
def get_class(kls):
    parts = kls.split(".")
    module = ".".join(parts[:-1])
    if check_module(module):
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
    else:
        raise Exception("No factor module:" + module)


def check_module(module_name):
    """检查模块时候能被导入而不用实际的导入模块"""
    return importlib.util.find_spec(module_name)


def get_factor_module(factor_name, loc):
    if '/' in loc:
        temp_loc, loc1 = loc.split('/')[:-1], loc.split('/')[-1]
        sys.path.append('/' + '/'.join(temp_loc))
    else:
        loc1 = loc
    # print(loc1,factor_name,check_module(".".join([loc1, factor_name])))
    if check_module(".".join([loc1, factor_name])):
        return loc1
    else:
        return None


def get_factor_class(factor_name, loc):
    module_name = get_factor_module(factor_name, loc)
    # print(module_name,factor_name,loc)
    if module_name:
        return get_class(".".join([module_name, factor_name, factor_name]))
    else:
        raise Exception("No factor found:" + factor_name)


def create_factor_instance(factor_class, **kwargs):
    factor_class_name = factor_class.__name__
    factor_instance = factor_class(**kwargs)
    return factor_instance


def restrict_datareader(fileloc):
    with open(fileloc, 'r') as b:
        val = b.read()
        for x in cross_datafuncs:
            if x in val:
                return False
    return True


# 这里主观上排除对tx，xq
def check(m, fileloc, logger):
    if not restrict_datareader(fileloc) and m.author not in ['tx', 'xq']:
        logger.error('文件中有非法数据读取')
        return False
    if m.author not in ['fc', 'hx', 'lzc', 'tx', 'xq', 'wyl']:
        logger.error('请重新定义author')
        return False
    if len(m.logic) == 0:
        logger.error('请输入因子逻辑')
        return False
    if m.freq not in ['daily', '30mins', '5mins', '1min']:
        logger.error('因子频率输入错误')
        return False
    return True


def split_dates(test_range, n):
    test_range = np.array(test_range)
    l = len(test_range)
    gap = l // n
    # if gap<2 and l>1:
    #     gap = 2
    temp = np.arange(l) % gap
    starts = test_range[temp == 0]
    ends = test_range[temp == gap - 1]
    if len(ends) == 0:
        ends = np.r_[ends[:-1], test_range[-1]]
    elif len(ends) != 0 and (ends[-1] != test_range[-1]):
        ends = np.r_[ends[:-1], test_range[-1]]
        starts = starts[:-1]
    return starts, ends


def get_kwarg_name(kwargs):
    kval = []
    for key, val in kwargs.items():
        if key not in ['start', 'end']:
            if isinstance(val, str):
                kval.append(val)
            else:
                kval.append(key + str(val))
    return sorted(kval)


def _cal_sub_factor(m, saveloc, name, notrun, **kwargs):
    start = kwargs['start'] if 'start' in kwargs else m.start
    end = kwargs['end'] if 'end' in kwargs else m.end
    kval = get_kwarg_name(kwargs)
    fileloc = saveloc + ('/{}_{}_{}' + '_{}' * len(kval) + '.npy').format(name, start, end, *kval)
    if os.path.exists(fileloc) and notrun:
        print(fileloc.split('/')[-1] + ' exists')
    else:
        finstance = create_factor_instance(m, **kwargs)
        for key, val in kwargs.items():
            assert finstance.__dict__[key] == val
        val = np.ascontiguousarray(finstance.result())
        if val.shape[-1] != len(finstance.code_list):
            print('数据code_list有误')
        else:
            np.save(fileloc, val.astype(np.float32))
            #print(('{}_{}_{}' + '_{}' * len(kval) + ' done').format(name, start, end, *kval))


def _cal_factor(logger, tstart, tend, m, filename, numd={'30mins': 6, '5mins': 10, '1min': 20, 'daily': 6},
                save_folder='factor_result', notrun=True, save=False, **kwargs):
    m.start, m.end = tstart, tend
    save_loc = '{}/{}/{}/{}_{}/{}'.format(m.loc, save_folder, m.freq, m.start, m.end, m.author)
    update_folder(save_loc)
    kval = get_kwarg_name(kwargs)
    if m.freq not in numd:
        finstance = create_factor_instance(m, **kwargs)
        # for key, val in kwargs.items():
        #     assert finstance.__dict__[key]==val
        res = finstance.result()
        res = res.astype('float32')
    else:
        logger.info('separate')
        test_range = get_date_range(m.start, m.end)
        num = numd[m.freq]
        starts, ends = split_dates(test_range, num)
        col = len(m.code_list)
        # if '/app/repository' not in sys.argv[0]:
        pool = mp.Pool(processes=num)
        for start, end in zip(starts, ends):
            pool.apply_async(_cal_sub_factor, (m, save_loc, filename, notrun), dict(start=start, end=end, **kwargs))
        pool.close()
        pool.join()

        res = np.empty((len(test_range), cross_freqs[m.freq], col), dtype='float32')
        for start, end in zip(starts, ends):
            try:
                startloc, endloc = test_range.index(start), test_range.index(end)
                shape = (endloc - startloc + 1, cross_freqs[m.freq], col)
                tempfile = save_loc + ('/{}_{}_{}' + '_{}' * len(kval) + '.npy').format(filename, start, end, *kval)
                fp = np.memmap(tempfile, dtype='float32', offset=128, shape=shape)
                res[startloc:endloc + 1, :, :] = fp[:]
                os.remove(tempfile)
            except:
                logger.error('数据计算不完整')
                return
    res[~np.isfinite(res)] = np.nan
    res = np.ascontiguousarray(res)
    if save:
        np.save(save_loc + ('/{}' + '_{}' * len(kval) + '.npy').format(filename, *kval), res.astype(np.float32))
    return res


# import logging
@time_limit(20 * 60, '因子计算超时')
@times('整体')
def cal_factor(fileloc=None, file=None, numd={'30mins': 20, '5mins': 20, '1min': 20, 'daily': 10},
               save_folder='factor_result',
               notrun=True, purerun=False, onlycheck=False,save =True, **kwargs):
    if fileloc == None:
        fileloc = '/'.join(sys.argv[0].split('/')[:-1])
        print('fileloc: ', fileloc)
    if file == None:
        file = sys.argv[0].split('/')[-1]
        print('file: ', file)

    try:
        m = get_factor_class(file.split('.')[0], fileloc)
    except:
        print('文件名、类名命名不一致；import未加入path；类定义等原因导致实例化失败')
        return

    filename = file.split('.')[0]
    tempstart = kwargs['start'] if 'start' in kwargs else cross_range[0]
    tempend = kwargs['end'] if 'end' in kwargs else cross_range[1]
    testt = get_date_range(tempstart, tempend)
    factor_info = {x: y for x, y in m.__dict__.items() if x in ['__module__'] + cross_params}
    for key, val in list(kwargs.items()):
        if (key not in cross_params) or (key in ['start', 'end']) :#or (m.__dict__.get(key, np.nan) == val):
            del kwargs[key]
        else:
            factor_info[key] = val

    kval = get_kwarg_name(kwargs)
    save_loc = '{}/{}/{}/{}_{}/{}'.format(m.loc, save_folder, m.freq, m.start, m.end, m.author)
    name = ('{}' + '_{}' * len(kval)).format(m.__name__, *kval)
    logger = logs(name, save_loc)
    factor_info['name'] = name
    factor_info['save_loc'] = save_loc
    if purerun:
        res = _cal_factor(logger, testt[0], testt[-1], m, filename, numd, save_folder, notrun, save, **kwargs)
        logger.info('purerun 成功')
        return factor_info,res
    else:
        if check(m, fileloc + '/' + file, logger):
            if len(testt) < 10:
                logger.error('时间区间过短，请重新设定')
                return False
            checkloc = (len(testt) // 3) * 2
            timelen = cross_freqs[m.freq] // 2
            checktime = cross_times[m.freq][timelen]
            checkval1 = _cal_factor(logger, testt[checkloc - 5], testt[checkloc], m, filename, {}, save_folder, notrun,
                                    False, **kwargs)
            checkval11 = _cal_factor(logger, testt[checkloc - 5], testt[checkloc], m, filename, {}, save_folder, notrun,
                                     False, mend=checktime, **kwargs)
            checkval2 = _cal_factor(logger, testt[checkloc - 7], testt[checkloc + 2], m, filename, {}, save_folder,
                                    notrun, False, **kwargs)[
                        2:-2, :, :]
            gapdate = abs(np.where(np.isfinite(checkval1), checkval1, 0) - np.where(np.isfinite(checkval2), checkval2,
                                                                                    0))  # [1:,:,:]
            gaptime = abs(
                np.where(np.isfinite(checkval1), checkval1, 0) - np.where(np.isfinite(checkval11), checkval11, 0))[-1,
                      max(0, timelen - 3):timelen, :]
            if np.nanmean(gapdate) > 1e-3 or np.nanmean(gaptime) > 1e-3 or np.nansum(np.isfinite(checkval1)) == 0:
                logger.error('extend_days 有误或者用到未来数据，\n具体情况: 日频 {}；分钟频 {}；数据非空 {}' \
                             .format(np.nanmean(gapdate), np.nanmean(gaptime), np.nansum(np.isfinite(checkval1))))
                return False
            elif checkval1.shape[-1] != len(m.code_list):
                logger.error('数据股票数未对齐')
                return False
            elif checkval1.shape[1] != cross_freqs[m.freq]:
                logger.error('数据频率有误 {}'.format(checkval1.shape[1]))
                return False
            else:
                if onlycheck:
                    logger.info('check 成功')
                    return True
                else:
                    del checkval1, checkval2
                    res = _cal_factor(logger = logger, tstart = testt[0], tend = testt[-1], m=m, filename = filename,
                                      numd = numd, save_folder=save_folder, notrun = notrun, save=save, **kwargs)

                    try:
                        if len(res):
                            save_range = get_date_range(cross_range[0], cross_range[1])
                            if testt[0] == save_range[0] and testt[-1] == save_range[-1]:
                                logger.info('因子存储成功！！')
                                return factor_info, res
                            else:
                                logger.info('因子计算成功，但是时间区间错误，请重新设置时间区间')
                                return  factor_info, res
                    except:
                        logger.info('因子存储失败，请查找原因')
        else:
            logger.info('因子存储失败，请查找原因')
