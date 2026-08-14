import pandas as pd
import os
start_date, end_date = 20160101, 20191231

basic_file_path = '/dfs/user/023859/share_file/for_sss/'
all_factor_path = '/data/user/factor_zooZZ/all_factor/931/'
md_path = '/dfs/user/023859/neptune/label_1430_1440_next_0930_0940/'

md = []
filenames = os.listdir(md_path)
for file in filenames:
    if file.endswith('.pkl'):
        md.append(pd.read_pickle(md_path+file))

md = pd.concat(md)[['pre_close','close','amt','adjfactor','buy_1430_1440_twap','sell_0930_0940_twap']].sort_index()