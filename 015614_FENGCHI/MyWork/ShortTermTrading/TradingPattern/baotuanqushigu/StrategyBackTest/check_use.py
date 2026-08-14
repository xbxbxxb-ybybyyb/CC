# @Time : 2020/7/22 9:46
# @Author : Zhichen Lu
# @File : check_use.py

import random
import time
from multiprocessing import Pool

from tqdm import tqdm


def myfunc(a):
    time.sleep(random.random())
    return a ** 2


if __name__ == '__main__':
    pool = Pool(2)
    '''
    for _ in tqdm(pool.imap_unordered(myfunc, range(100)), total=100):
        pass
    '''
    pbar = tqdm(total=10)


    def update(*a):
        pbar.update()
        # tqdm.write(str(a))


    for i in range(pbar.total):
        pool.apply_async(myfunc, args=(i,), callback=update)
    # tqdm.write('scheduled')
    pool.close()
    pool.join()
