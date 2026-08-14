from multiprocessing import Pool
import dask
import time


def multidask(dask_name, dask_list):
    lines = len(dask_list)
    batches = []
    t = time.time()
    print(f'{dask_name}: 等待{lines}条线程全部完成...')
    for j in range(lines):
        batches.append(dask.delayed(dask_list[j][0])(*dask_list[j][1]))
    dask.compute(batches)
    t = round(time.time() - t, 3)
    print(f'{dask_name}: 多线程结束, 用时{t}秒')


def multiprocess(lines, func, iterable, *args):
    pool = Pool(processes=lines)
    print('多进程启动')
    pool_apply_async = {}
    for j in range(lines):
        sub_iter = iterable[j::lines]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args + (j,))
    pool.close()
    print('等待%s个进程全部完成...' % lines)
    pool.join()
    print('多进程结束！')
    return pool_apply_async


def play_aimr(idd, parts, func, iter_list):
    todo_list = iter_list[idd::parts]
    for package in todo_list:
        try:
            if isinstance(package, (tuple, list)):
                func(*package)
            else:
                func(package)
        except:
            print('ERROR', package)
            continue

