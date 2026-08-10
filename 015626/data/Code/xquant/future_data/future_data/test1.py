import pandas as pd
import numpy as np
import datetime
from multifactor.IO import IO
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import itertools
import multifactor.utility.dt as udt
from multiprocessing import Pool
import glob

path_list = glob.glob('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock/*.pkl')

def retrieve_path(path):
    print(path)
    df = pd.read_pickle(path, compression='gzip')
    df = df.loc[20171201:]
    if len(df) > 0:
        df.to_pickle(path.replace('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND','/arch1/group/800466/warehouse/prod/MD/CHINA_STOCK'), compression='gzip')

with Pool(24) as pool:
    pool.map(retrieve_path, path_list)