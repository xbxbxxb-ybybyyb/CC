# from joblib import Parallel,delayed
import multiprocessing
import numpy as np
pool = multiprocessing.Pool(4)

factor_df_list = [pool.apply_async(np.log,args=(i,)).get() for i in range(1,60)]