import pandas as pd
from multiprocessing import Pool
import os

def getna(path):
    print(path)
    df = pd.read_pickle(path, compression = 'gzip')
    return df[df.isnull().T.any()]
    
root_path = '/data/group/800080/warehouse/test/LOCAL_DATA/CSV/WIND/MINUTE/stock'
pickle_path_list = [os.path.join(root_path,i) for i in os.listdir(root_path)]

with Pool(processes = 24) as pool:
    df_list = pool.map(getna, pickle_path_list)
    allnadf = pd.concat(df_list)
allnadf.to_csv('/data/user/015626/check_data/minute2013na.csv')
print(allnadf)