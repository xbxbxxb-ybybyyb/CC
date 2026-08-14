import multiprocessing
import time

def wait_and_print(x):
    time.sleep(1)
    print(x)
    return x

if __name__ == '__main__':
    pool = multiprocessing.Pool(processes = 2)
    results = []
    for i in range(2):
        result = pool.apply_async(wait_and_print, args=(i,))
        results.append(result)
    pool.close()
    pool.join()
    for result in results:
        print(result.get())