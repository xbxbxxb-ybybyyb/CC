# coding: utf-8
# Author：fengchi863
# Date ：2022/9/5 10:36
from multiprocessing import Pool

class SpeedUtil:
    def __init__(self):
        self.stock_name_dict = None

    @staticmethod
    def multiprocess(kernal_num, func, iterable, *args):
        pool = Pool(kernal_num)
        print('多进程启动')
        pool_apply_async = {}
        parts = len(iterable) // kernal_num
        remainder = len(iterable) % kernal_num
        iter_start = 0
        for j in range(kernal_num):
            if remainder > 0:
                iter_end = iter_start + parts + 1
                remainder = remainder - 1
            else:
                iter_end = iter_start + parts
            sub_iter = iterable[iter_start: iter_end]
            pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args)
            iter_start = iter_end
        pool.close()
        pool.join()
        print('多进程结束')
        return pool_apply_async

SpeedUtil = SpeedUtil()